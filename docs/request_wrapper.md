
# RequestWrapper 說明

`RequestWrapper` 是系統中每個請求（gRPC 呼叫）所對應的封裝物件，它的目的是讓請求在進入 batch 系統前後的生命週期被追蹤與管理。

---

## 🎯 目的與設計理念

### 1. 封裝單次請求資料
- 包含經過前處理後的 `frame`
- 用來進入 YOLO 模型推論

### 2. 支援非同步結果傳遞
- 透過 `result_queue` 等待推論結果
- `SkeletonFrame` 不用知道是何時被處理，只需等結果出現

### 3. 加入請求時間戳記
- `enqueue_time` 用來計算等待時間與排程公平性
- 可以針對 trigger_type 做統計與優化

### 4. 統一記錄請求 log
- 每個請求都綁定一個 logger 實例
- 可記錄 client_ip, wait_ms, inference_ms 等各階段資訊

---

## 📦 典型流程中負責什麼？

| 階段 | `RequestWrapper` 中負責的部分 |
|------|-------------------------------|
| PoseService 收到請求 | 建立 `RequestWrapper(frame)` |
| 加入佇列 | `queue.put(wrapper)` |
| 被 BatchProcessor 處理時 | 提取 `frame` 做推論 |
| 推論後放回結果 | `wrapper.result_queue.put(result)` |
| 寫入 log | `wrapper.logger.write()` |

---

## ✅ 總結

你可以把 `RequestWrapper` 想成一個：

> 🧱「請求容器」：從前處理 → 排程 → 推論 → 回應，整個過程的記憶單位

這樣設計可以保持流程清晰、資料一致、易於除錯與擴充。
