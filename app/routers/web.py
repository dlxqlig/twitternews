from fastapi import APIRouter, Depends, Request, BackgroundTasks, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Tweet, SystemSetting
from app.services.scheduler import check_lists, update_job_interval, get_check_interval
from app.config import settings
from datetime import datetime, date
from zoneinfo import ZoneInfo

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def to_shanghai(value):
    if not value:
        return ""
    if value.tzinfo is None:
        # Assume UTC if naive
        value = value.replace(tzinfo=ZoneInfo("UTC"))
    return value.astimezone(ZoneInfo("Asia/Shanghai"))

templates.env.filters["to_shanghai"] = to_shanghai

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == settings.ADMIN_PASSWORD:
        request.session["user"] = "admin"
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request, "error": "密码错误"})

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    if not get_current_user(request):
        return RedirectResponse(url="/login")
    
    # Get latest date (in Shanghai time)
    latest_date = db.query(func.date(Tweet.created_at, '+8 hours')).order_by(func.date(Tweet.created_at, '+8 hours').desc()).first()
    
    if latest_date:
        return RedirectResponse(url=f"/date/{latest_date[0]}")
    else:
        # No data yet
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "tweets": [], 
            "dates": [], 
            "current_date": date.today().isoformat(),
            "min_score": 0.0
        })

@router.get("/date/{date_str}")
def read_date(date_str: str, request: Request, min_score: float = 0.0, db: Session = Depends(get_db)):
    if not get_current_user(request):
        return RedirectResponse(url="/login")
        
    # Get all available dates for sidebar (in Shanghai time)
    available_dates = db.query(func.date(Tweet.created_at, '+8 hours').label('date'))\
        .group_by(func.date(Tweet.created_at, '+8 hours'))\
        .order_by(func.date(Tweet.created_at, '+8 hours').desc())\
        .all()
    
    dates_list = [d[0] for d in available_dates]
    
    # Get tweets for specific date (in Shanghai time)
    tweets = db.query(Tweet)\
        .filter(func.date(Tweet.created_at, '+8 hours') == date_str)\
        .filter(Tweet.relevance_score >= min_score)\
        .order_by(Tweet.created_at.desc())\
        .all()
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "tweets": tweets, 
        "dates": dates_list,
        "current_date": date_str,
        "min_score": min_score
    })

@router.post("/refresh")
async def refresh_data(background_tasks: BackgroundTasks, request: Request):
    if not get_current_user(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    background_tasks.add_task(check_lists)
    return {"message": "刷新已开始"}

@router.get("/settings")
def settings_page(request: Request, db: Session = Depends(get_db)):
    if not get_current_user(request):
        return RedirectResponse(url="/login")
    
    interval = get_check_interval()
    return templates.TemplateResponse("settings.html", {"request": request, "interval": interval})

@router.post("/settings/update")
def update_settings(request: Request, interval: int = Form(...), db: Session = Depends(get_db)):
    if not get_current_user(request):
        return RedirectResponse(url="/login")
    
    # Update DB
    setting = db.query(SystemSetting).filter(SystemSetting.key == "check_interval_minutes").first()
    if not setting:
        setting = SystemSetting(key="check_interval_minutes", value=str(interval))
        db.add(setting)
    else:
        setting.value = str(interval)
    db.commit()
    
    # Update Scheduler
    update_job_interval(interval)
    
    return RedirectResponse(url="/settings", status_code=status.HTTP_303_SEE_OTHER)
