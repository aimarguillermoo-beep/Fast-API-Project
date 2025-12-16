from fastapi import FastAPI


app = FastAPI()


@app.get("/Hello World")
def hello_World():
        return {"message": "Hello World"}
    
    