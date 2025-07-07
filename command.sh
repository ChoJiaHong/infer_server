#取得批次設定 (GET /config/batching):
curl -X GET http://127.0.0.1:8000/config/batching

#更新批次設定 (POST /config/batching): 假設你想將 batch_size 設為 10，queue_timeout 設為 0.05：
curl -X POST http://127.0.0.1:8000/config/batching \
     -H "Content-Type: application/json" \
     -d '{"batch_size": 1, "queue_timeout": 0.01}'


kubectl cp ../my_infer_server_v2 pose-1-30561:/app

kubectl cp  pose-1-30561:/app/my_infer_server_v2/logs  ../my_infer_server_v2/logs
