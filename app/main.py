from fastapi import FastAPI
from app.api.job_routers import router

app = FastAPI(title="Transaction Intelligence API")


@app.get("/")
def root():
    return {
        "message": "Alemeno Backend Assignment API Running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(
    router,
    prefix="/jobs",
    tags=["Jobs"]
)
