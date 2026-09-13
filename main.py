from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import bcrypt
from database import SessionLocal, Foerderung, Admin, Anfrage, Base, engine

app = FastAPI(title="Förderungs-API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== SICHERHEIT =====
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    db = SessionLocal()
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    db.close()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    password_bytes = credentials.password.encode('utf-8')
    hash_bytes = admin.password_hash.encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hash_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ===== DATENBANK BEIM START INITIALISIEREN =====
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    
    # Förderungen prüfen und befüllen
    db = SessionLocal()
    count = db.query(Foerderung).count()
    
    if count == 0:
        from seed_data import seed_database
        seed_database()
        print("✅ Datenbank wurde automatisch befüllt!")
    
    # Admin prüfen und anlegen
    admin_count = db.query(Admin).count()
    db.close()
    
    if admin_count == 0:
        db = SessionLocal()
        
        username = "admin"
        password = "architekt2026"
        
        password_bytes = password.encode('utf-8')
        password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        
        admin = Admin(username=username, password_hash=password_hash)
        db.add(admin)
        db.commit()
        db.close()
        
        print(f"✅ Admin '{username}' automatisch angelegt!")

# ===== MODELLE =====

class FoerderungResponse(BaseModel):
    id: int
    name: str
    massnahme: str
    gebaeudetyp: str
    zuschuss: str
    details: str
    max_foerderung: Optional[float] = None

class FoerderungRequest(BaseModel):
    massnahme: str
    gebaeudetyp: str

class FoerderungCreate(BaseModel):
    name: str
    massnahme: str
    gebaeudetyp: str
    zuschuss: str
    details: str
    max_foerderung: Optional[float] = None

class AnfrageCreate(BaseModel):
    name: str
    email: str
    telefon: Optional[str] = None
    massnahme: str
    gebaeudetyp: str
    baujahr: Optional[int] = None
    ergebnis: Optional[str] = None

class AnfrageResponse(BaseModel):
    id: int
    name: str
    email: str
    telefon: Optional[str] = None
    massnahme: str
    gebaeudetyp: str
    baujahr: Optional[int] = None
    ergebnis: Optional[str] = None
    erstellt_am: str    

# ===== ÖFFENTLICHE ENDPUNKTE =====

@app.get("/")
def read_root():
    return {"message": "Förderungs-API läuft! 🚀"}

@app.get("/foerderungen", response_model=List[FoerderungResponse])
def get_all_foerderungen():
    db = SessionLocal()
    result = db.query(Foerderung).all()
    db.close()
    return result

@app.post("/foerderungen/check", response_model=List[FoerderungResponse])
def check_foerderung(request: FoerderungRequest):
    db = SessionLocal()
    result = db.query(Foerderung).filter(
        Foerderung.massnahme == request.massnahme,
        Foerderung.gebaeudetyp == request.gebaeudetyp
    ).all()
    db.close()

    if not result:
        raise HTTPException(status_code=404, detail="Keine Förderungen gefunden.")
    return result

# ===== ADMIN-ENDPUNKTE (nur mit Login) =====

@app.get("/admin/foerderungen", response_model=List[FoerderungResponse])
def admin_get_all(username: str = Depends(verify_admin)):
    """Alle Förderungen (Admin)"""
    db = SessionLocal()
    result = db.query(Foerderung).all()
    db.close()
    return result

@app.post("/admin/foerderungen", response_model=FoerderungResponse)
def admin_create_foerderung(data: FoerderungCreate, username: str = Depends(verify_admin)):
    """Neue Förderung anlegen (Admin)"""
    db = SessionLocal()
    foerderung = Foerderung(**data.dict())
    db.add(foerderung)
    db.commit()
    db.refresh(foerderung)
    db.close()
    return foerderung

@app.put("/admin/foerderungen/{foerderung_id}", response_model=FoerderungResponse)
def admin_update_foerderung(foerderung_id: int, data: FoerderungCreate, username: str = Depends(verify_admin)):
    """Förderung bearbeiten (Admin)"""
    db = SessionLocal()
    foerderung = db.query(Foerderung).filter(Foerderung.id == foerderung_id).first()
    
    if not foerderung:
        db.close()
        raise HTTPException(status_code=404, detail="Förderung nicht gefunden.")
    
    for key, value in data.dict().items():
        setattr(foerderung, key, value)
    
    db.commit()
    db.refresh(foerderung)
    db.close()
    return foerderung

@app.delete("/admin/foerderungen/{foerderung_id}")
def admin_delete_foerderung(foerderung_id: int, username: str = Depends(verify_admin)):
    """Förderung löschen (Admin)"""
    db = SessionLocal()
    foerderung = db.query(Foerderung).filter(Foerderung.id == foerderung_id).first()
    
    if not foerderung:
        db.close()
        raise HTTPException(status_code=404, detail="Förderung nicht gefunden.")
    
    db.delete(foerderung)
    db.commit()
    db.close()
    return {"message": f"Förderung {foerderung_id} wurde gelöscht."}

# ===== ANFRAGEN =====

@app.post("/anfragen", response_model=AnfrageResponse)
def create_anfrage(data: AnfrageCreate):
    """Neue Anfrage speichern (öffentlich)"""
    from datetime import datetime
    
    db = SessionLocal()
    anfrage = Anfrage(
        name=data.name,
        email=data.email,
        telefon=data.telefon,
        massnahme=data.massnahme,
        gebaeudetyp=data.gebaeudetyp,
        baujahr=data.baujahr,
        ergebnis=data.ergebnis,
        erstellt_am=datetime.now().strftime("%d.%m.%Y %H:%M")
    )
    db.add(anfrage)
    db.commit()
    db.refresh(anfrage)
    db.close()
    return anfrage

@app.get("/admin/anfragen", response_model=List[AnfrageResponse])
def admin_get_anfragen(username: str = Depends(verify_admin)):
    """Alle Anfragen (Admin)"""
    db = SessionLocal()
    result = db.query(Anfrage).order_by(Anfrage.id.desc()).all()
    db.close()
    return result

@app.delete("/admin/anfragen/{anfrage_id}")
def admin_delete_anfrage(anfrage_id: int, username: str = Depends(verify_admin)):
    """Anfrage löschen (Admin)"""
    db = SessionLocal()
    anfrage = db.query(Anfrage).filter(Anfrage.id == anfrage_id).first()
    
    if not anfrage:
        db.close()
        raise HTTPException(status_code=404, detail="Anfrage nicht gefunden.")
    
    db.delete(anfrage)
    db.commit()
    db.close()
    return {"message": f"Anfrage {anfrage_id} wurde gelöscht."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)