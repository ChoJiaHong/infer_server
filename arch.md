/pose_grpc_server/
├── model/
│   └── batch_worker.py        # 包含 YOLO 模型推論邏輯
├── processor/
│   └── batch_processor.py     # 負責聚合 queue、觸發 batch 推論
├── service/
│   ├── pose_service.py        # gRPC Service：SkeletonFrame 處理 (batch)
│   └── pose_service_no_batch.py  # 不使用 batch 的版本
├── utils/
│   ├── timing.py              # 裝飾器
│   └── formatter.py           # YOLO 結果轉 JSON
└── main.py                    # 啟動入口（serve）
