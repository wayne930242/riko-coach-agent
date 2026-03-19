#!/usr/bin/env python3
"""
Stop Hook — 儲存本次 session 的重要資訊到今日日誌
從 stdin 讀取 Claude 的 stop 事件 JSON
"""

import json
import sys
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
JOURNAL_DIR = PROJECT_DIR / "data" / "journal"


def append_session_note(note: str):
    """將 session 摘要附加到今日日誌的隨筆區塊"""
    today = date.today().isoformat()
    journal_file = JOURNAL_DIR / f"{today}.md"
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M")

    session_entry = f"\n- {timestamp} [Session] {note}"

    if journal_file.exists():
        content = journal_file.read_text(encoding="utf-8")
        if "## 📝 隨筆" in content:
            content = content.replace("## 📝 隨筆", f"## 📝 隨筆{session_entry}", 1)
        else:
            content += f"\n\n## 📝 隨筆{session_entry}\n"
    else:
        content = f"# 健康日誌｜{today}\n\n---\n\n## 📝 隨筆{session_entry}\n"

    journal_file.write_text(content, encoding="utf-8")


def main():
    try:
        data = json.loads(sys.stdin.read())
        # stop_reason 可能是 "end_turn", "max_tokens" 等
        stop_reason = data.get("stop_reason", "")

        # 只在正常結束時記錄（避免錯誤時寫入）
        if stop_reason in ("end_turn", ""):
            append_session_note("對話結束")
    except Exception:
        # Hook 失敗不應影響主流程，靜默退出
        pass


if __name__ == "__main__":
    main()
