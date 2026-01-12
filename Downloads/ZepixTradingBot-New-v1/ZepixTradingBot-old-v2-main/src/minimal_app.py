from fastapi import FastAPI

app = FastAPI(title="Minimal Test App")

@app.get("/ping")
async def ping():
    return {"pong": True}
