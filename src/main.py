import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/index")
def index():

somthing other
    return {"text": "Hello, world!"}


def main():
    uvicorn.run("src.main:app", reload=True)


if __name__ == "__main__":
    main()
