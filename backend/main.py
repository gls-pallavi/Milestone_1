from fastapi import FastAPI
from routes import router
from db import engine, Base

app = FastAPI(title="WellBot Backend")
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong!"}
