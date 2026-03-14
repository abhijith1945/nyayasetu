import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = None  # type: ignore

if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_supabase_url":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Supabase: %s", str(e))
else:
    logger.warning("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_KEY in .env")

# Import jobs
from jobs.scheduler import check_sla_breaches, check_fake_closures

# APScheduler
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NyayaSetu backend...")
    try:
        scheduler.add_job(check_sla_breaches, "interval", minutes=5, id="sla_check", replace_existing=True)
        scheduler.add_job(check_fake_closures, "interval", minutes=2, id="fake_closure_check", replace_existing=True)
        # Cluster detection runs every 10 minutes via async job
        # We schedule it as a sync wrapper since APScheduler BackgroundScheduler needs sync functions
        def _run_cluster_sync():
            import asyncio
            from jobs.scheduler import run_cluster_detection
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(run_cluster_detection())
                loop.close()
            except Exception as e:
                logger.error("Cluster detection sync wrapper error: %s", str(e))

        scheduler.add_job(_run_cluster_sync, "interval", minutes=10, id="cluster_detection", replace_existing=True)
        scheduler.start()
        logger.info("Background scheduler started with 3 jobs")
    except Exception as e:
        logger.error("Failed to start scheduler: %s", str(e))

    yield

    # Shutdown
    try:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title="NyayaSetu API",
    description="Public Grievance Intelligence Platform for India",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers.grievances import router as grievances_router
from routers.ai import router as ai_router
from routers.dashboard import router as dashboard_router
from routers.legal import router as legal_router

app.include_router(grievances_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(legal_router)


@app.get("/")
async def root():
    return {
        "success": True,
        "data": {
            "name": "NyayaSetu API",
            "version": "1.0.0",
            "status": "running",
            "supabase_connected": supabase is not None,
        },
        "error": None,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
