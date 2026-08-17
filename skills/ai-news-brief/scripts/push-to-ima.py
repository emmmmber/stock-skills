#!/usr/bin/env python3
"""把 Markdown 简报投递到腾讯 IMA 个人知识库的指定文件夹。

走的是纯 JSON 路径：notes/import_doc 建笔记 → wiki/add_knowledge 以 media_type=11
把笔记挂进知识库文件夹。避开了 create_media + COS 二进制上传那条路（需要 COS 签名
和临时密钥，依赖更重、更容易出错）。

凭据从环境变量读，不接受命令行传参，避免进 shell history：
    IMA_CLIENT_ID / IMA_API_KEY   （在 https://ima.qq.com/agent-interface 申请）

用法：
    # 先探测，确认知识库和文件夹能被正确识别（不写入任何东西）
    python push-to-ima.py --probe

    # 预演，打印将要发出的请求但不真正提交
    python push-to-ima.py 周报.md --folder 知识总结 --dry-run

    # 正式投递
    python push-to-ima.py 周报.md --kb 我的知识库 --folder 知识总结

零第三方依赖，只用标准库。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://ima.qq.com"
MEDIA_TYPE_NOTE = 11        # 笔记
CONTENT_FORMAT_MARKDOWN = 1  # 写入接口目前只支持 Markdown


class ImaError(RuntimeError):
    pass


def call(path, payload, *, client_id, api_key, timeout=30):
    """POST 一个 JSON 请求，返回解析后的 body。"""
    url = f"{BASE_URL}/{path.lstrip('/')}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "ima-openapi-clientid": client_id,
            "ima-openapi-apikey": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise ImaError(f"{path} HTTP {e.code}\n{body}") from None
    except urllib.error.URLError as e:
        raise ImaError(f"{path} 网络不可达：{e.reason}") from None

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        raise ImaError(f"{path} 返回的不是 JSON：\n{raw[:500]}") from None

    return unwrap(path, body)


def unwrap(path, body):
    """剥掉可能存在的响应信封。

    IMA 各接口的信封字段官方文档没有统一说明，这里做容错：认识常见的
    ret_code/code/errcode 组合，都不匹配就原样返回，交给调用方处理。
    """
    if not isinstance(body, dict):
        return body

    for code_key in ("ret_code", "code", "errcode", "error_code"):
        if code_key in body:
            code = body[code_key]
            if code not in (0, "0", None, ""):
                msg = ""
                for msg_key in ("message", "msg", "errmsg", "error_msg"):
                    if body.get(msg_key):
                        msg = body[msg_key]
                        break
                raise ImaError(f"{path} 业务失败 {code_key}={code} {msg}\n{json.dumps(body, ensure_ascii=False)[:500]}")
            for data_key in ("data", "result", "response"):
                if isinstance(body.get(data_key), dict):
                    return body[data_key]
            return body
    return body


def pick(item, *keys, default=None):
    """从字典里按优先级取第一个存在且非空的键。"""
    for k in keys:
        v = item.get(k)
        if v not in (None, ""):
            return v
    return default


def paginate(path, payload, list_keys, *, client_id, api_key, limit=50, max_pages=20):
    """游标翻页，把各页的列表拼起来。"""
    out, cursor, pages = [], "", 0
    while pages < max_pages:
        body = call(path, {**payload, "cursor": cursor, "limit": limit},
                    client_id=client_id, api_key=api_key)
        chunk = None
        for k in list_keys:
            if isinstance(body.get(k), list):
                chunk = body[k]
                break
        if chunk is None:
            raise ImaError(
                f"{path} 响应里找不到列表字段 {list_keys}，实际字段：{list(body)}\n"
                f"（接口返回结构可能已变，用 --probe 看原始 JSON）"
            )
        out.extend(chunk)
        pages += 1
        if body.get("is_end") or not body.get("next_cursor"):
            break
        cursor = body["next_cursor"]
    return out


def find_knowledge_base(name, *, client_id, api_key):
    """按名称找知识库；name 为空则返回全部候选。"""
    bases = paginate("openapi/wiki/v1/get_addable_knowledge_base_list", {},
                     ["knowledge_base_list", "list", "infos", "knowledge_bases"],
                     client_id=client_id, api_key=api_key)
    if not name:
        return None, bases
    for kb in bases:
        if pick(kb, "name", "title") == name:
            return pick(kb, "id", "knowledge_base_id"), bases
    for kb in bases:  # 退而求其次：包含匹配
        if name in str(pick(kb, "name", "title", default="")):
            return pick(kb, "id", "knowledge_base_id"), bases
    return None, bases


def find_folder(kb_id, name, *, client_id, api_key):
    """在知识库根目录下按名称找文件夹。"""
    items = paginate("openapi/wiki/v1/get_knowledge_list", {"knowledge_base_id": kb_id},
                     ["knowledge_list", "list", "items"],
                     client_id=client_id, api_key=api_key)
    folders = [i for i in items if str(pick(i, "id", "folder_id", default="")).startswith("folder_")]
    if not name:
        return None, folders
    for f in folders:
        if pick(f, "name", "title") == name:
            return pick(f, "id", "folder_id"), folders
    return None, folders


def main():
    ap = argparse.ArgumentParser(description="把 Markdown 简报投递到 IMA 知识库")
    ap.add_argument("file", nargs="?", help="要投递的 Markdown 文件")
    ap.add_argument("--kb", help="知识库名称（不传则用第一个可用知识库）")
    ap.add_argument("--kb-id", help="直接指定知识库 ID，跳过按名称查找")
    ap.add_argument("--folder", default="知识总结", help="目标文件夹名（默认：知识总结）")
    ap.add_argument("--folder-id", help="直接指定文件夹 ID，跳过按名称查找")
    ap.add_argument("--title", help="笔记标题（默认取文件名）")
    ap.add_argument("--probe", action="store_true", help="只列出知识库和文件夹，不写入")
    ap.add_argument("--dry-run", action="store_true", help="打印将要发出的写请求但不提交")
    args = ap.parse_args()

    client_id = os.environ.get("IMA_CLIENT_ID")
    api_key = os.environ.get("IMA_API_KEY")
    if not client_id or not api_key:
        sys.exit("缺少凭据：请设置环境变量 IMA_CLIENT_ID 和 IMA_API_KEY\n"
                 "申请地址 https://ima.qq.com/agent-interface")
    creds = {"client_id": client_id, "api_key": api_key}

    try:
        kb_id = args.kb_id
        if not kb_id:
            kb_id, bases = find_knowledge_base(args.kb, **creds)
            if args.probe or not kb_id:
                print("可用知识库：")
                for kb in bases:
                    print(f"  {pick(kb, 'id', 'knowledge_base_id')}  {pick(kb, 'name', 'title')}")
                if not args.probe:
                    sys.exit(f"\n找不到名为「{args.kb}」的知识库，用上面的 ID 配合 --kb-id 重试")
                if not kb_id and bases:
                    kb_id = pick(bases[0], "id", "knowledge_base_id")

        folder_id = args.folder_id
        if not folder_id and kb_id:
            folder_id, folders = find_folder(kb_id, args.folder, **creds)
            if args.probe or not folder_id:
                print(f"\n知识库 {kb_id} 根目录下的文件夹：")
                for f in folders:
                    print(f"  {pick(f, 'id', 'folder_id')}  {pick(f, 'name', 'title')}")
                if not args.probe:
                    sys.exit(f"\n找不到名为「{args.folder}」的文件夹，"
                             f"请先在 IMA 里建好，或用 --folder-id 指定")

        if args.probe:
            print("\n探测完成，未写入任何内容。")
            return

        if not args.file:
            sys.exit("请指定要投递的 Markdown 文件（或加 --probe 只做探测）")

        with open(args.file, encoding="utf-8") as fh:
            content = fh.read()
        title = args.title or os.path.splitext(os.path.basename(args.file))[0]

        note_payload = {"content_format": CONTENT_FORMAT_MARKDOWN, "content": content}
        link_payload = {
            "media_type": MEDIA_TYPE_NOTE,
            "title": title,
            "knowledge_base_id": kb_id,
        }
        if folder_id:
            link_payload["folder_id"] = folder_id

        if args.dry_run:
            print("[dry-run] POST openapi/note/v1/import_doc")
            print(json.dumps({**note_payload, "content": f"<{len(content)} 字符>"},
                             ensure_ascii=False, indent=2))
            print("\n[dry-run] POST openapi/wiki/v1/add_knowledge")
            print(json.dumps({**link_payload, "media_id": "<上一步返回的 doc_id>"},
                             ensure_ascii=False, indent=2))
            return

        note = call("openapi/note/v1/import_doc", note_payload, **creds)
        doc_id = pick(note, "doc_id", "id")
        if not doc_id:
            raise ImaError(f"import_doc 没返回 doc_id，实际响应：{json.dumps(note, ensure_ascii=False)[:500]}")
        print(f"✓ 笔记已创建 doc_id={doc_id}")

        link_payload["media_id"] = doc_id
        call("openapi/wiki/v1/add_knowledge", link_payload, **creds)
        print(f"✓ 已挂入知识库 {kb_id}" + (f" / 文件夹 {folder_id}" if folder_id else " 根目录"))

    except ImaError as e:
        sys.exit(f"失败：{e}")


if __name__ == "__main__":
    main()
