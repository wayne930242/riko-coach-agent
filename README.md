# Coach Kai 個人健康助理

一個示範 Claude Code Workspace 功能的健康助理專案，整合 Garmin 健康數據、多角色 AI 專家、智慧日誌管理。

## 功能一覽

| 功能 | 說明 |
|------|------|
| 🏃 Garmin 數據讀取 | 步數、心率、睡眠、Body Battery、活動記錄 |
| 📓 智慧日誌 | `/add-journal` 一鍵記錄心情、健身、飲食 |
| 📋 週度計劃審查 | `/plan-reviewer` 三位專家綜合分析 |
| 🎓 學術搜尋 | 引用 PubMed / Semantic Scholar 科學文獻 |
| 🔄 記憶持久化 | 每次開啟自動載入健康檔案與近期日誌 |

---

## 快速開始

### 1. 安裝 uv（跨平台 Python 套件管理）

**macOS / Linux：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows：**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 安裝 MCP Server 依賴

```bash
uv sync --directory mcp-server
```

### 3. 設定 Garmin 帳號

複製範例設定檔並填入帳號：

```bash
cp .env.example .env
```

編輯 `.env`：
```
GARMIN_EMAIL=你的@email.com
GARMIN_PASSWORD=你的密碼
```

### 4. 啟動 Claude Code

```bash
claude
```

Claude Code 會自動載入 MCP server 和 hooks。

---

## 示範流程

以下是一個完整的操作示範，使用虛構用戶「阿明」（28 歲，上班族，想減重 5 公斤）。

---

### Step 1：建立健康檔案

輸入指令：
```
/say-hi
```

Coach Kai 會開始問你問題。**照著這些回答輸入：**

```
問：你叫什麼名字？
答：阿明

問：幾歲？
答：28 歲

問：主要目標？
答：A（減脂瘦身）

問：運動習慣？
答：幾乎沒有，偶爾走路，一週大概 1-2 次

問：飲食習慣？
答：A（一般飲食，沒有限制，但常吃外食）

問：特殊注意事項？
答：沒有，但怕無聊的訓練，做不下去

問：有沒有 Garmin？
答：有，Garmin Venu 3
```

**預期結果：** `data/profile.md` 自動建立完成

---

### Step 2：記錄今日心情

輸入指令：
```
/add-journal mood 今天工作壓力有點大，但還是撐過去了。晚餐吃了排骨便當，有點後悔。
```

**預期結果：** `data/journal/2026-XX-XX.md` 建立，包含心情記錄

---

### Step 3：詢問今日健康狀況

直接和 Coach Kai 對話：
```
今天的身體狀況怎麼樣？
```

Coach Kai 會呼叫 MCP 工具讀取 Garmin 數據，回報今日步數、心率、Body Battery 等。

**預期結果：** 看到類似這樣的回覆：
> 「今天步數 3,241 步，還差一點喔！Body Battery 剩 28，算是偏低。靜息心率 61，不錯。今晚建議輕度活動或提早休息，讓身體充電 🔋」

---

### Step 4：問健身建議（觸發後台 Agent）

```
我想今天做個訓練，有什麼建議？
```

**預期結果：** Coach Kai 委派給 `fitness-coach` 後台 Agent，根據 Body Battery 決定訓練強度，回傳具體建議

---

### Step 5：問飲食（觸發營養師 Agent）

```
我晚餐想吃麥當勞，沒關係吧？
```

**預期結果：** 委派給 `nutritionist` Agent，給出具體的點餐建議（例如選哪個比較好）

---

### Step 6：週度計劃審查

```
/plan-reviewer
```

**預期結果：** 三位後台專家分別分析本週的飲食、訓練、數據趨勢，產出下週三件事

---

### Step 7：查學術資料（觸發研究助理 Agent）

```
有科學依據說明睡前吃東西真的會變胖嗎？
```

**預期結果：** `research-assistant` 搜尋 PubMed，找到相關論文摘要，Coach Kai 用口語化方式解釋

---

## 專案結構說明

```
claude-code-workshop/
├── CLAUDE.md                    ← Coach Kai 人設（唯一主人格）
├── .env                         ← Garmin 帳密（不進 git）
├── .env.example                 ← 範例設定
├── .mcp.json                    ← MCP Server 設定
├── mcp-server/
│   ├── server.py                ← Garmin 數據 + 日誌 MCP 工具
│   └── pyproject.toml           ← Python 依賴
├── hooks/
│   ├── session_start.py         ← SessionStart：載入健康檔案 + 近期日誌
│   ├── session_stop.py          ← Stop：記錄 session 結束
│   └── save_research.py         ← PostToolUse：自動儲存學術搜尋結果
├── data/
│   ├── profile.md               ← 使用者健康檔案（/say-hi 建立）
│   ├── journal/                 ← 每日日誌（YYYY-MM-DD.md）
│   └── research/                ← 學術搜尋快取
└── .claude/
    ├── settings.json            ← Hooks 設定
    ├── agents/
    │   ├── nutritionist.md      ← 營養分析（後台工具）
    │   ├── fitness-coach.md     ← 訓練計劃（後台工具）
    │   ├── sport-scientist.md   ← 數據分析（後台工具）
    │   └── research-assistant.md ← 學術搜尋（後台工具）
    ├── skills/
    │   ├── say-hi/              ← 建立健康檔案
    │   ├── add-journal/         ← 新增日誌（帶參數）
    │   └── plan-reviewer/       ← 週度計劃審查（fork context）
    └── rules/
        └── journal-format.md    ← 日誌格式規範（path-scoped）
```

## Claude Code Workspace 功能示範對照

| Claude Code 功能 | 本專案對應 |
|------------------|-----------|
| `CLAUDE.md` 人設 | Coach Kai 主人格設定 |
| Agents（後台專家）| 營養師、健身教練、科學家、研究助理 |
| Skills（技能指令）| `/say-hi`、`/add-journal`、`/plan-reviewer` |
| Rules（路徑規則）| 日誌格式規範（只在讀日誌時觸發）|
| MCP Server | Garmin 健康數據工具 |
| Hooks（生命週期）| SessionStart 載入記憶、Stop 寫入日誌 |
| Fork Context | `/plan-reviewer` 獨立 context 執行 |
