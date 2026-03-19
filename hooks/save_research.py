#!/usr/bin/env python3
"""
PostToolUse Hook — 儲存學術搜尋結果到本地
當 research-assistant agent 使用 WebFetch 或 WebSearch 時觸發
"""

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_DIR / "data" / "research"


def main():
    try:
        data = json.loads(sys.stdin.read())
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        tool_response = data.get("tool_response", {})

        # 只處理 WebSearch 和 WebFetch 的結果
        if tool_name not in ("WebSearch", "WebFetch"):
            return

        RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{tool_name.lower()}.md"
        output_file = RESEARCH_DIR / filename

        query = tool_input.get("query") or tool_input.get("url") or "unknown"

        # 取得回傳內容
        if isinstance(tool_response, dict):
            content = tool_response.get("content") or json.dumps(tool_response, ensure_ascii=False)
        else:
            content = str(tool_response)

        # 只儲存有內容且看起來像學術搜尋的結果
        academic_keywords = ["pubmed", "semanticscholar", "openalex", "europepmc", "ncbi", "doi", "abstract"]
        query_lower = query.lower()
        content_lower = content.lower() if isinstance(content, str) else ""

        if not any(kw in query_lower or kw in content_lower for kw in academic_keywords):
            return  # 不是學術搜尋，跳過

        output = f"""# 學術搜尋結果

**工具**：{tool_name}
**查詢**：{query}
**時間**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{content}
"""
        output_file.write_text(output, encoding="utf-8")

    except Exception:
        pass


if __name__ == "__main__":
    main()
