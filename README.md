# 相田理子 健康助理 Agent

<img src="https://static.wikia.nocookie.net/kurokonobasuke/images/7/75/Riko_Aida_anime.png/revision/latest/scale-to-width-down/268?cb=20121105194434" align="right" width="160" alt="相田理子">

> 「🧐 聽好了，你現在的狀態是⋯⋯」

以《黑子的籃球》相田理子為主人格的個人健康助理。講話直接，不接受模糊目標，但你做到了她會比你還高興。

---

## 安裝（Plugin）

```bash
/plugin marketplace add wayne930242/riko-coach-agent
/plugin install riko-health-coach@riko-health-coach
```

安裝完成後仍需手動設定 MCP Server（Garmin 帳號），見下方快速開始步驟 1–3。

---

## 快速開始

### 1. 安裝 uv

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

```bash
cp .env.example .env
# 編輯 .env，填入 GARMIN_EMAIL 和 GARMIN_PASSWORD
```

### 4. 啟動

```bash
claude
```

---

## 常用指令

| 指令 | 說明 |
|------|------|
| `/say-hi` | 建立你的健康檔案，理子會逐一詢問基本資料、身體狀況、運動環境、飲食習慣，並由科學家做初始分析 |
| `/add-journal [類型] [內容]` | 新增今日日誌。類型可為 `mood`、`workout`、`food`、`sleep`、`note`，每天只有一份日誌 |
| `/plan-training [1d\|1w\|1m]` | 生成個人化訓練飲食菜單，依參數產出單日、週計劃或月計劃，儲存到 `data/plans/` |
| `/plan-reviewer` | 週度健康審查，從營養、訓練、數據三個角度綜合分析近期狀況，產出下週三件事 |

---

## 後台專家

直接對話時，理子會視情況委派給後台專家，使用者無需手動呼叫：

| 專家 | 負責範圍 |
|------|---------|
| 營養師 | 飲食分析、熱量規劃、外食建議 |
| 訓練師 | 訓練菜單、動作選擇、強度調整 |
| 科學家 | Garmin 數據解讀、睡眠分析、過度訓練預警 |
| 研究員 | PubMed / Semantic Scholar 學術文獻搜尋 |

---

## 專案結構

```
.
├── CLAUDE.md                        ← 相田理子人設
├── .mcp.json                        ← MCP Server 設定
├── mcp-server/                      ← Garmin 數據 + 日誌工具
├── hooks/                           ← SessionStart / Stop / 研究存檔
├── data/
│   ├── profile.md                   ← 健康檔案（/say-hi 建立）
│   ├── gym-profile.md               ← 健身環境記錄
│   ├── journal/                     ← 每日日誌
│   ├── plans/                       ← 訓練飲食菜單
│   └── research/                    ← 學術搜尋快取
└── .claude/
    ├── agents/                      ← 四位後台專家
    ├── skills/                      ← say-hi / add-journal / plan-training / plan-reviewer
    ├── rules/                       ← 日誌格式規範
    └── knowledge/exercises/         ← 動作資料庫（有氧、徒手、啞鈴、健身房）
```
