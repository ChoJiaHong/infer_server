

---

# 模型擴充與處理流程切換指南

本文件說明如何在現有模組化架構下，**擴充新的推論模型與對應的處理流程**（例如從 Pose 模型擴充至 Gesture、Object Detection 模型），而不需重寫主流程邏輯。

---

## 📁 系統結構總覽

目前關鍵模組如下：

```
project/
├── model/                # 模型執行邏輯
├── processor/            # batch queue 管理
├── service/              # gRPC 接口邏輯
├── utils/
│   ├── preprocessor.py   # 前處理策略類（依模型任務分支）
│   └── postprocessor.py  # 後處理策略類（解析模型輸出）
├── main.py               # 伺服器啟動入口
└── config.py             # 基本參數（batch_size、timeout 等）
```

---

## 🔁 目標：支援多任務推論（Pose / Gesture / Object）

你可以為不同任務註冊一組：

* Preprocessor
* Postprocessor
* （可選）ModelWorker

---

## 🧩 1. 新增前處理類別（Preprocessor）

在 `utils/preprocessor.py` 中定義：

```python
class GesturePreprocessor(Preprocessor):
    def process(self, image_data):
        # decode + resize to 224x224 + normalize
        ...
```

---

## 🧠 2. 新增後處理類別（Postprocessor）

在 `utils/postprocessor.py` 中定義：

```python
class GesturePostprocessor(Postprocessor):
    def process(self, result):
        # 將 YOLO 輸出轉換為 gesture 格式 JSON
        ...
```

---

## ⚙️ 3. 新建服務邏輯（可選）

若需分別 expose 多個任務，可建立：

```python
class GestureDetectionService(proto.pose_pb2_grpc.MirrorServicer):
    def __init__(self, ...):
        self.preprocessor = GesturePreprocessor()
        self.postprocessor = GesturePostprocessor()
        ...
```

然後在 `main.py` 中綁定對應 service：

```python
proto.pose_pb2_grpc.add_MirrorServicer_to_server(PoseDetectionService(...), server)
proto.pose_pb2_grpc.add_MirrorServicer_to_server(GestureDetectionService(...), server)
```

---

## ☁️ 4. 其他擴充建議

| 模組          | 擴充方向                                      |
| ----------- | ----------------------------------------- |
| `config.py` | 加入任務選擇變數，如 `TASK="pose"`                  |
| `main.py`   | 根據 `config.TASK` 動態選用 Service 類           |
| `proto.pose_pb2`  | 定義多個 RPC 方法，如 `PoseFrame`, `GestureFrame` |

---

## ✅ 結論

本架構透過策略模式與模組化設計，使你能：

* 快速切換處理邏輯
* 支援多模型與多任務
* 提高維護性與可測試性

若需加入新模型，只需擴充相對應 Pre/Post 類，主流程無需變動。

---


