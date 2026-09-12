"""
Enterprise Python Demo API
A small FastAPI service used to demonstrate a full GitLab CI/CD pipeline:
source control -> code review -> CI -> security scan -> CD -> release ->
change mgmt -> monitoring -> rollback -> compliance/audit.
"""
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db, engine, Base
from app import models
from app.config import settings

app = FastAPI(
    title="Enterprise Python Demo",
    description="Demo service for GitLab CI/CD pipeline showcase",
    version=os.getenv("APP_VERSION", "0.0.0-dev"),
)

# Tables are created via Alembic migrations in real environments;
# this call is safe for local/dev quick-start only.
Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["monitoring"])
def health_check():
    """Used by Kubernetes liveness/readiness probes and pipeline smoke tests."""
    return {
        "status": "ok",
        "version": app.version,
        "environment": settings.environment,
        "time": datetime.utcnow().isoformat(),
    }


@app.get("/version", tags=["monitoring"])
def version():
    """Confirms what build/tag is actually running -- used by the CD deploy job
    and by the release/audit process to prove what went live."""
    return {
        "version": app.version,
        "commit": os.getenv("CI_COMMIT_SHORT_SHA", "local"),
        "pipeline": os.getenv("CI_PIPELINE_ID", "local"),
        "environment": settings.environment,
    }


@app.get("/items", tags=["items"])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()


@app.post("/items", tags=["items"])
def create_item(name: str, db: Session = Depends(get_db)):
    if not name or len(name) > 100:
        raise HTTPException(status_code=400, detail="invalid item name")
    item = models.Item(name=name, created_at=datetime.utcnow())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items/{item_id}", tags=["items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item
