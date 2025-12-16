from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routers import web
from app.database import engine, Base
from app.services.scheduler import start_scheduler
from app.config import settings
import logging

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Twitter List Monitor")

# Add session middleware for login
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Mount static files if needed (optional, but good for custom css/js)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web.router)

@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
