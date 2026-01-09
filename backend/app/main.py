from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os, shutil, time

from . import models
from .db import SessionLocal, engine

app = FastAPI(title="OceanSense API")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # backend/app
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- STATIC ----------------
# Serve frontend assets
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# ---------------- ROOT ----------------
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{page}.html", include_in_schema=False)
def serve_pages(page: str):
    file_path = os.path.join(FRONTEND_DIR, f"{page}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

# ---------------- DATABASE ----------------
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- API ----------------
@app.post("/api/issues")
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    severity: str = Form("low"),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    photo_path = None
    if photo and photo.filename:
        filename = f"{int(time.time())}_{photo.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_path = path

    issue = models.Issue(
        title=title,
        description=description,
        lat=lat,
        lon=lon,
        severity=severity,
        photo_path=photo_path,
    )

    db.add(issue)
    db.commit()
    db.refresh(issue)

    return {"id": issue.id, "status": "created"}

@app.get("/api/issues")
def list_issues(db: Session = Depends(get_db)):
    return db.query(models.Issue).order_by(models.Issue.created_at.desc()).all()

from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- AUTH MODELS ----------------
class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ---------------- AUTH ROUTES ----------------
@app.post("/api/auth/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # check if user exists
    user = db.execute(
        "SELECT * FROM users WHERE email = :email",
        {"email": data.email}
    ).fetchone()

    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(data.password)

    db.execute(
        "INSERT INTO users (email, password) VALUES (:email, :password)",
        {"email": data.email, "password": hashed}
    )
    db.commit()

    return {"status": "account created"}

@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        "SELECT * FROM users WHERE email = :email",
        {"email": data.email}
    ).fetchone()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"status": "login successful"}
