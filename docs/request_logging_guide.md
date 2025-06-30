

---

# 🧾 Per-Request 日誌模組使用說明 (`RequestLogger`)

本文件說明如何使用模組化的 `RequestLogger` 來記錄並分析每筆請求在 AI 推論流程中的延遲與耗時。

---

## 🎯 目的

`RequestLogger` 用於精確記錄每個請求在下列階段的耗時：

| 階段名稱          | 說明                  |
| ------------- | ------------------- |
| `enqueue`     | 請求進入 batch queue 時間 |
| `infer_start` | batch 開始推論的時間       |
| `infer_end`   | batch 結束推論的時間       |
| `post_start`  | 開始進行後處理的時間          |
| `post_end`    | 後處理完成並準備回應的時間       |

---

## 📦 使用方式

### 1. 匯入模組

```python
from utils.request_logger import RequestLogger
```

---

### 2. 在 `RequestWrapper` 中初始化 Logger

```python
self.logger = RequestLogger()
self.logger.mark("enqueue")
```

---

### 3. 在 `_batch_loop` 中標記推論時段

```python
wrapper.logger.mark("infer_start")
results = self.worker.predict(batch_images)
wrapper.logger.mark("infer_end")
```

---

### 4. 在 `SkeletonFrame()` 標記後處理

```python
wrapper.logger.mark("post_start")
processed_result = self.postprocessor.process(raw_result)
wrapper.logger.mark("post_end")
```

---

### 5. 匯出與顯示結果（可選）

```python
wrapper.logger.export_csv()      # 將結果寫入 logs/request_trace.csv
wrapper.logger.print_summary()   # 輸出精簡摘要到終端
```

---

## 🧪 輸出格式（CSV）

| request\_id | start\_ts | end\_ts | wait\_ms | infer\_ms | postprocess\_ms | total\_cycle\_ms |
| ----------- | --------- | ------- | -------- | --------- | --------------- | ---------------- |
| ab12cd34    | 2025-01-01 00:00:00 | 2025-01-01 00:00:01 | 11.64 | 23.08 | 9.94 | 39.78 |

---

## 📁 檔案結構建議

```
project/
├── utils/
│   └── request_logger.py     ← 日誌模組位置
├── logs/
│   └── request_trace.csv     ← 自動產生的追蹤紀錄
├── docs/
│   └── request_logging_guide.md
```

---

## 📊 日誌分析

可使用 `utils/analyze_request_trace.py` 讀取 `logs/request_trace.csv` 並輸出平均耗時統計：

```bash
python utils/analyze_request_trace.py
```
