import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/index")
def index():
    return {"text": "Hello, world!"}


def main():
    uvicorn.run("main:app", reload=True)


if __name__ == "__main__":
    main()
