"""AlphaQuantPro backend — AI quant strategy workbench (simulation only).

DISCLAIMER: This software is for research and education. It is not financial
advice. Backtests and simulations do not guarantee future performance.
No real-money trading is possible in this MVP.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analysis, backtests, market_data, paper_runs, settings, strategies
from .seed import seed_examples
from .storage.database import SessionLocal, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_examples(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AlphaQuantPro API",
    description=(
        "AI quant trading / strategy agent workbench. Simulation and paper "
        "trading only — real-money execution is not available in the MVP."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies.router)
app.include_router(backtests.router)
app.include_router(paper_runs.router)
app.include_router(market_data.router)
app.include_router(analysis.router)
app.include_router(settings.router)


@app.get("/")
def root():
    return {
        "name": "AlphaQuantPro API",
        "version": "0.1.0",
        "disclaimer": "Not financial advice. Simulation only — no real-money trading in MVP.",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
