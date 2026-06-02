import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
from apscheduler.schedulers.background import BackgroundScheduler
from middleware.rate_limit import add_rate_limiting

# Load environment variables
_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_env_path)

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
from jobs.scheduler import check_sla_breaches, check_fake_closures, generate_predictions

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

        def _run_railway_cluster_sync():
            import asyncio
            from jobs.scheduler import run_railway_cluster_detection
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(run_railway_cluster_detection())
                loop.close()
            except Exception as e:
                logger.error("Railway cluster detection sync wrapper error: %s", str(e))

        scheduler.add_job(_run_cluster_sync, "interval", minutes=10, id="cluster_detection", replace_existing=True)
        scheduler.add_job(_run_railway_cluster_sync, "interval", minutes=10, id="railway_cluster_detection", replace_existing=True)
        scheduler.add_job(generate_predictions, "interval", hours=6, id="predictions", replace_existing=True)
        scheduler.start()
        logger.info("Background scheduler started with 5 jobs")
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

# Rate limiting
limiter = add_rate_limiting(app)

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
from routers.railway import router as railway_router
from routers.audit import router as audit_router
from routers.predictions import router as predictions_router
from routers.auth import router as auth_router
from routers.officer import router as officer_router
from routers.agents import router as agents_router

app.include_router(auth_router)
app.include_router(officer_router)
app.include_router(grievances_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(legal_router)
app.include_router(railway_router)
app.include_router(audit_router)
app.include_router(predictions_router)
app.include_router(agents_router)


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


@app.post("/api/setup-v2")
async def setup_v2(db_password: str = ""):
    """Create V2 tables. Provide your Supabase database password."""
    if not db_password:
        return {"success": False, "error": "Provide db_password query param. Find it at: Supabase Dashboard -> Settings -> Database -> Connection string"}
    try:
        import psycopg2
        project_ref = "evobwnzwqfrotsttkgok"
        v2_sql = open("schema.sql").read().split("-- V2 EXPANSION")[1] if "-- V2 EXPANSION" in open("schema.sql").read() else ""
        if not v2_sql:
            return {"success": False, "error": "Could not find V2 SQL in schema.sql"}

        # Wrap CREATE POLICY in DO blocks to avoid duplicate errors
        import re
        policies = re.findall(r'CREATE POLICY "([^"]+)" ON (\w+) FOR ALL USING \(true\) WITH CHECK \(true\);', v2_sql)
        for policy_name, table_name in policies:
            old = f'CREATE POLICY "{policy_name}" ON {table_name} FOR ALL USING (true) WITH CHECK (true);'
            new = f'DO $$ BEGIN CREATE POLICY "{policy_name}" ON {table_name} FOR ALL USING (true) WITH CHECK (true); EXCEPTION WHEN duplicate_object THEN NULL; END $$;'
            v2_sql = v2_sql.replace(old, new)

        conn = None
        for host, port, user in [
            (f"db.{project_ref}.supabase.co", 5432, "postgres"),
            ("aws-0-ap-south-1.pooler.supabase.com", 5432, f"postgres.{project_ref}"),
            ("aws-0-ap-southeast-1.pooler.supabase.com", 5432, f"postgres.{project_ref}"),
            ("aws-0-us-east-1.pooler.supabase.com", 5432, f"postgres.{project_ref}"),
        ]:
            try:
                conn = psycopg2.connect(host=host, port=port, dbname="postgres", user=user, password=db_password, connect_timeout=10)
                break
            except Exception:
                continue
        if not conn:
            return {"success": False, "error": "Could not connect to database. Check your password."}
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(v2_sql)
        cur.close()
        conn.close()
        return {"success": True, "data": {"message": "V2 tables created successfully!"}, "error": None}
    except ImportError:
        return {"success": False, "error": "psycopg2 not installed. Run: pip install psycopg2-binary"}
    except Exception as e:
        return {"success": False, "error": str(e)}
