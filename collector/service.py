from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/frame")
def get_frame():
    return{{"message": "post frames"}}

@app.get("/frame")
def get_frame():
    return{{"message": "get frames"}}