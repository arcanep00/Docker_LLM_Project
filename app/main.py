from fastapi import FastAPI
from app.api.job_routers import router

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Alemeno Backend Assignment API Running"
    }


app.include_router(
    router,
    prefix="/jobs",
    tags=["Jobs"]
)