from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.signals import router as signals_router

app = FastAPI(title="Crypto Signals Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://quantum-ai-world.com",
        "https://www.quantum-ai-world.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals_router)
