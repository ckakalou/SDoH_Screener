# Created by Christine Kakalou on 10/9/26
# Project: SDoH_Screener

from fastapi import FastAPI

app = FastAPI(
    title="SDoH Screener API",
    description="Backend API for the EU/Greek Social Determinants of Health screener.",
    version="0.1.0",
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

