from fastapi import FastAPI
import uvicorn
from app.routers import users, login, receipt


app = FastAPI()

app.include_router(users.router)
app.include_router(login.router)
app.include_router(receipt.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
