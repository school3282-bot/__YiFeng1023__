# test1.py 程式說明

## 概述

這是一個 **Open WebUI Filter（過濾器）插件**的範例程式。

Open WebUI 的 Filter 插件允許開發者在對話流程的兩個關鍵時間點插入自訂邏輯：
1. **inlet**：使用者訊息送出前（前處理）
2. **outlet**：AI 回應返回後（後處理）

---

## 程式架構

```
Filter
├── Valves（管理員全域設定）
├── UserValves（使用者個人設定）
├── __init__()（初始化）
├── inlet()（入口攔截器）
└── outlet()（出口攔截器）
```

---

## 類別說明

### `Filter`
插件的主體類別，Open WebUI 會自動識別並載入此類別。

---

### `Valves`（管理員設定）

| 欄位 | 預設值 | 說明 |
|------|--------|------|
| `priority` | `0` | 過濾器執行優先順序，數字越小越優先 |
| `max_turns` | `8` | 全域最大對話輪數上限 |

由管理員在後台設定，對所有使用者生效。

---

### `UserValves`（使用者設定）

| 欄位 | 預設值 | 說明 |
|------|--------|------|
| `max_turns` | `4` | 使用者自訂的最大對話輪數 |

每位使用者可自行調整，但實際生效值不會超過管理員設定的上限。

---

### `__init__()`

初始化方法，建立 `Valves` 實例以載入全域設定。

```python
self.valves = self.Valves()
```

> 備註：若需要自訂檔案處理邏輯，可啟用 `self.file_handler = True`，WebUI 會將檔案操作交由此插件處理。

---

### `inlet(body, __user__)` — 入口攔截器

**執行時機**：使用者訊息送往 AI 模型之前。

**主要邏輯**：
1. 取得目前對話的訊息列表
2. 計算實際允許的最大輪數：`min(使用者設定, 全域設定)`
3. 若訊息數量超過上限，拋出例外，阻止對話繼續

```python
max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)
if len(messages) > max_turns:
    raise Exception(f"Conversation turn limit exceeded. Max turns: {max_turns}")
```

**範例情境**：
- 管理員設定 `max_turns = 8`
- 使用者設定 `max_turns = 4`
- 實際上限 = `min(4, 8)` = **4 輪**

---

### `outlet(body, __user__)` — 出口攔截器

**執行時機**：AI 模型回應之後、顯示給使用者之前。

**目前行為**：僅印出除錯資訊，直接回傳原始回應，未做任何修改。

可在此處擴充：
- 過濾敏感詞
- 記錄對話日誌
- 修改或格式化 AI 回應內容

---

## 對話輪數限制邏輯圖

```
使用者送出訊息
      ↓
   inlet()
      ↓
計算 max_turns = min(user.max_turns, global.max_turns)
      ↓
訊息數 > max_turns？
   ↙         ↘
  是           否
  ↓             ↓
拋出例外      送往 AI 模型
（阻止對話）       ↓
              AI 回應
                ↓
            outlet()
                ↓
          顯示給使用者
```

---

## 使用的套件

| 套件 | 用途 |
|------|------|
| `pydantic` | 資料驗證與設定管理（`BaseModel`, `Field`） |
| `typing` | 型別提示（`Optional`） |
