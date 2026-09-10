from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal, Foerderung, Base, engine

app = FastAPI(title="Förderungs-API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== DATENBANK BEIM START INITIALISIEREN =====
@app.on_event("startup")
def startup_event():
    # Tabellen erstellen (falls nicht vorhanden)
    Base.metadata.create_all(bind=engine)
    
    # Prüfen, ob Daten vorhanden sind
    db = SessionLocal()
    count = db.query(Foerderung).count()
    db.close()
    
    if count == 0:
        # Datenbank befüllen
        from seed_data import seed_database
        seed_database()
        print("✅ Datenbank wurde automatisch befüllt!")

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

# ===== ENDPUNKTE =====

@app.get("/")
def read_root():
    return {"message": "Förderungs-API läuft! 🚀"}

@app.get("/foerderungen", response_model=List[FoerderungResponse])
def get_all_foerderungen():
    db = SessionLocal()
    result = db.query(Foerderung).all()
    db.close()
    return result

@app.get("/admin/seed")
def admin_seed():
    """Manuelles Befüllen der Datenbank"""
    from seed_data import seed_database
    seed_database()
    return {"message": "Datenbank wurde befüllt!"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)