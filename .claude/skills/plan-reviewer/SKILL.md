---
name: plan-reviewer
description: 健康計劃週度審查。從三位後台專家的角度（營養、訓練、科學數據）綜合分析近期健康狀況，給出平衡的建議與下週重點。使用獨立 context 執行，避免干擾主對話。
allowed-tools: Read Glob mcp__health-coach__get_stats_range mcp__health-coach__get_sleep mcp__health-coach__get_recent_activities mcp__health-coach__list_journals mcp__health-coach__read_journal
context: fork
disable-model-invocation: true
---

# 健康計劃週度審查

## 步驟 1：蒐集數據

1. 用 `get_stats_range` 取得**過去 7 天**的健康數據
2. 用 `get_sleep` 取得**過去 7 天**的睡眠數據
3. 用 `get_recent_activities` 取得**最近 10 筆**活動
4. 用 `list_journals` 列出本週日誌，再用 `read_journal` 逐一讀取

如果 MCP 工具無法使用，只用日誌數據進行分析，並在報告中說明數據來源限制。

## 步驟 2：三視角分析

### 🥗 營養視角（猫猫）
- 本週飲食記錄顯示哪些模式？
- 熱量與蛋白質攝取是否支撐訓練量？
- 下週飲食一個具體改進重點

### 💪 訓練視角（Levi）
- 本週訓練量和強度是否合理？
- Body Battery 和活動安排是否匹配？
- 下週訓練一個具體調整建議

### 🔬 數據視角（紅莉栖）
- 睡眠趨勢：本週睡眠品質整體評估
- 壓力和恢復的平衡狀態
- 數據顯示需要特別注意的一個警示

## 步驟 3：輸出報告

以下格式輸出週度報告：

```markdown
# 週度健康報告｜[日期範圍]

## 本週亮點 ✨
[1-2 個做得好的地方]

## 三位專家的分析

### 🥗 營養
[飲食分析與建議]

### 💪 訓練
[訓練分析與建議]

### 🔬 數據
[數據解讀與警示]

## 下週三件事 🎯
1. [最重要的第一件事]
2. [第二件事]
3. [第三件事]

---
*報告由 /plan-reviewer 自動產生*
```

報告輸出後，詢問使用者是否要儲存到本週日誌中。
