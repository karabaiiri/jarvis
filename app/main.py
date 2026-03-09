from fastapi import FastAPI
from app.config import settings
from app.api.health import router as health_router
from app.api.journal import router as journal_router
from app.api.market import router as market_router
from app.api.preopen import router as preopen_router
from app.api.outcomes import router as outcomes_router
from app.api.review import router as review_router
from app.api.performance import router as performance_router
from app.api.admin import router as admin_router
from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(journal_router)
app.include_router(market_router)
app.include_router(preopen_router)
app.include_router(outcomes_router)
app.include_router(review_router)
app.include_router(performance_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
