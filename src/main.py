import uvicorn
from fastapi import FastAPI

app = FastAPI()

something


@app.get("/index")
def index():
    return {"text": "Hello, world!"}


def main():
    uvicorn.run("src.main:app", reload=True)


if __name__ == "__main__":
    main()
