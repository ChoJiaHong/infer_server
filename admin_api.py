from fastapi import FastAPI, HTTPException
from pydantic.v1 import BaseModel
from batch_config import global_batch_config
from typing import Union
from metrics.max_load_estimator import MaxLoadEstimator
from config import settings
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


class EstimateRequest(BaseModel):
    max_rps: int = 50
    step: int = 5
    duration: float = 5.0


@app.post("/system/estimate_throughput")
def estimate_throughput(req: EstimateRequest):
    estimator = MaxLoadEstimator(
        target=f"localhost:{settings.gRPC_port}",
        duration=req.duration,
        step=req.step,
        max_rps=req.max_rps,
    )
    max_rps = estimator.estimate()
    return {"max_rps": max_rps}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
