
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Livre, Reservation
from datetime import datetime
from auth.jwt_handler import verify_token

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/reservations")
def reserver_livre(request: Request, id_livre: int = Form(...), db: Session = next(get_db())):
    # Récupérer l'utilisateur connecté depuis le JWT
    token = request.cookies.get("access_token")
    payload = verify_token(token)
    if not payload:
        return HTMLResponse("Utilisateur non authentifié", status_code=401)
    id_adherent = payload["user_id"]

    # Vérifier le livre
    livre = db.query(Livre).filter(Livre.id == id_livre).first()
    if not livre or livre.disponibilite <= 0:
        return HTMLResponse("Livre indisponible", status_code=400)

    # Vérifier si l'utilisateur a déjà réservé ce livre
    existing = db.query(Reservation).filter(
        Reservation.id_adherent == id_adherent,
        Reservation.id_livre == id_livre,
        Reservation.statut == "validée"
    ).first()
    if existing:
        return HTMLResponse("Vous avez déjà réservé ce livre", status_code=400)

    # Créer la réservation
    reservation = Reservation(
        id_adherent=id_adherent,
        id_livre=id_livre,
        date_reservation=datetime.now(),
        statut="validée"
    )
    db.add(reservation)

    # Mettre à jour la disponibilité
    livre.availability_num -= 1
    db.commit()

    # Rediriger avec confirmation
    response = RedirectResponse(url="/home", status_code=302)
    response.set_cookie(key="msg", value="Réservation réussie !", httponly=True)
    return response
