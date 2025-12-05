from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, db
from .db import SessionLocal, engine
import shutil, os
from dotenv import load_dotenv
load_dotenv()
# app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="OceanSense API")

# resolve directories reliably (uses _file_ correctly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # -> path/to/project/app
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
INDEX_PATH = os.path.join(FRONTEND_DIR, "index.html")

# mount static folder if it exists (frontend/static)
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(INDEX_PATH)

# fallback for any other path so SPA routes work
@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    return FileResponse(INDEX_PATH)



models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='OceanSense API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def get_db():
    db_sess = SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post('/api/issues')
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    severity: str = Form('low'),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    photo_path = None
    if photo:
        filename = f"{int(db.execute('select extract(epoch from now())').scalar())}_{photo.filename}"
        out_path = os.path.join(UPLOAD_DIR, filename)
        with open(out_path, 'wb') as f:
            shutil.copyfileobj(photo.file, f)
        photo_path = out_path

    issue = models.Issue(title=title, description=description, lat=lat, lon=lon, severity=severity, photo_path=photo_path)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return {"id": issue.id, "status": "created"}

@app.get('/api/issues')
def list_issues(db: Session = Depends(get_db)):
    return db.query(models.Issue).order_by(models.Issue.created_at.desc()).all()

@app.get('/api/issues/{issue_id}')
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail='Not found')
    return issue

@app.post('/api/issues/{issue_id}/status')
def update_status(issue_id:int, status: str = Form(...), db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail='Not found')
    issue.status = status
    db.commit()
    return {"status":"ok"}
