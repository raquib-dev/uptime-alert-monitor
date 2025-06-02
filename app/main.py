import os
from sqlalchemy import func, Integer
from app.logger import logger
from app.routes import endpoints
from app.routes import auth
from app.models import Base, Target, PingHistory, User
from fastapi import FastAPI, Request, Depends
from sqlalchemy.future import select
from app.scheduler import start_scheduler
from fastapi.responses import HTMLResponse
from app.database import engine, SessionLocal
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from app.utils.deps import get_current_user
from app.startup import create_default_admin


app = FastAPI(title="Uptime Alert Monitor")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Allow cross-origin requests for frontend if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Uptime Monitor...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_default_admin()
    await start_scheduler()

@app.get("/")
def root():
    return {"status": "Uptime Monitor API is running 🚀"}

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    async with SessionLocal() as session:
        result = await session.execute(select(Target))
        targets = result.scalars().all()

        uptime_map = {}
        for t in targets:
            q = await session.execute(
                select(
                    func.count(PingHistory.id),
                    func.sum(PingHistory.status.cast(Integer))
                ).where(PingHistory.target_id == t.id)
            )
            total, up_count = q.first()
            if total and up_count is not None:
                uptime = (up_count / total) * 100
                uptime_map[t.id] = f"{uptime:.1f}%"
            else:
                uptime_map[t.id] = "N/A"

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "targets": targets,
        "uptime_map": uptime_map
    })

@app.get("/target/{target_id}/history", response_class=HTMLResponse)
async def history_chart(target_id: int, request: Request, range: str = "all", interval: int = 1):
    async with SessionLocal() as session:
        stmt = select(PingHistory).options(selectinload(PingHistory.target)).where(
            PingHistory.target_id == target_id
        ).order_by(PingHistory.checked_at.asc())

        if range != "all":
            now = datetime.now()
            if range == "1h":
                cutoff = now - timedelta(hours=1)
            elif range == "24h":
                cutoff = now - timedelta(days=1)
            elif range == "7d":
                cutoff = now - timedelta(days=7)
            else:
                cutoff = None

            if cutoff:
                stmt = stmt.where(PingHistory.checked_at >= cutoff)

        q = await session.execute(stmt)
        history = q.scalars().all()

        # Apply interval skipping
        history = history[::interval]

    return templates.TemplateResponse("history_chart.html", {
        "request": request,
        "history": history,
        "selected_range": range,
        "selected_interval": str(interval),
    })
