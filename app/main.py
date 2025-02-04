from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"info": "Welcome to Hisaab Backend", "docs": "http://127.0.0.1:8000/docs/"}