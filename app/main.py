from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Alemeno Backend Assignment API Running"
    }
