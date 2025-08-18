
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Livre, Reservation, Adherent
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/livre/{id}", response_class=HTMLResponse)
def livre_detail(request: Request, id: int, db: Session = next(get_db())):
    livre = db.query(Livre).filter(Livre.id == id).first()
    if not livre:
        return HTMLResponse("Livre non trouvé", status_code=404)
    return templates.TemplateResponse("livre.html", {"request": request, "livre": livre})

@app.post("/api/reservations")
def reserver_livre(id_livre: int = Form(...), db: Session = next(get_db())):
    # Ici il faut récupérer l'utilisateur connecté (ex: via JWT)
    id_adherent = 1  # exemple temporaire, remplacer par l'ID réel
    livre = db.query(Livre).filter(Livre.id == id_livre).first()
    
    if livre.disponibilite <= 0:
        return HTMLResponse("Livre indisponible", status_code=400)

    # Vérifier si l'utilisateur a déjà réservé ce livre
    existing = db.query(Reservation).filter(
        Reservation.id_livre == id_livre,
        Reservation.id_adherent == id_adherent,
        Reservation.statut == "validée"
    ).first()
    if existing:
        return HTMLResponse("Vous avez déjà réservé ce livre.", status_code=400)

    # Créer la réservation
    reservation = Reservation(
        id_adherent=id_adherent,
        id_livre=id_livre,
        date_reservation=datetime.now(),
        statut="validée"
    )
    db.add(reservation)
    livre.disponibilite -= 1
    db.commit()
    
    return RedirectResponse(url=f"/livre/{id_livre}", status_code=302)
