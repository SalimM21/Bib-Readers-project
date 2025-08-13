from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import uvicorn

from models import Adherent

app = FastAPI()

# Créer les tables si ce n’est pas fait
Base.metadata.create_all(bind=engine)

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/register")
def register_adherent(adherent_data: dict, db: Session = Depends(get_db)):
    # Exemple insertion avec ORM
    adherent = Adherent(**adherent_data)
    db.add(adherent)
    db.commit()
    db.refresh(adherent)
    return {"id": adherent.id, "message": "Adhérent enregistré avec succès"}

