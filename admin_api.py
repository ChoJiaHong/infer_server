from fastapi import FastAPI, HTTPException
from pydantic.v1 import BaseModel
from batch_config import global_batch_config
from typing import Union
app = FastAPI()

class BatchConfigUpdate(BaseModel):
    batch_size: Union[int, None] = None
    queue_timeout: Union[float, None] = None

@app.get("/config/batching")
def get_batch_config():
    return global_batch_config.as_dict()

@app.post("/config/batching")
def update_batch_config(update: BatchConfigUpdate):
    print(update)  # 打印接收到的資料
    if update.batch_size is None and update.queue_timeout is None:
        raise HTTPException(status_code=400, detail="No parameters provided")
    global_batch_config.update(update.batch_size, update.queue_timeout)
    return global_batch_config.as_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
