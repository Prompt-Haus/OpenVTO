"""OpenVTO Playground API - Virtual Try-On as a Service."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import openvto
from openvto import OpenVTO

from app import dependencies
from app.routers import assets, generate, health

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize OpenVTO client on startup."""
    dependencies.vto_client = OpenVTO(provider="google")
    yield
    dependencies.vto_client = None


app = FastAPI(
    title="OpenVTO Playground",
    description="Virtual try-on API powered by generative AI",
    version=openvto.__version__,
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(assets.router)
app.include_router(generate.router)
