# Created by Christine Kakalou on 10/9/26
# Project: SDoH_Screener
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENER_FILE = PROJECT_ROOT / "sdoh_screener_eu_gr_v2.json"


app = FastAPI(
    title="SDoH Screener API",
    description="Backend API for the EU/Greek Social Determinants of Health screener.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/screener")
def get_screener() -> dict[str, Any]:
    with SCREENER_FILE.open(encoding="utf-8") as file:
        return json.load(file)
