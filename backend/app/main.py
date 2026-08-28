from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.lifespan import lifespan
from app.routes.router import api_router
from app.middleware import setup_middleware


app = FastAPI(
    title="Demo API",
    description="Demo Project For Fastapi",
    version="1.0.0",
    lifespan=lifespan,
)

setup_middleware(app)
app.include_router(api_router)

# Instrument Prometheus metrics endpoint (/metrics)
Instrumentator().instrument(app).expose(app)


@app.get('/')
async def root():
    return "Hello From Yasin Arafat."

@app.get("/health")
async def health_check():
    return {"status": "ok"}
