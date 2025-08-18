from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

from models import Adherent
from schemas import AdherentCreate

app = FastAPI()

# Créer les tables si ce n’est pas fait
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home_page(request: Request):
    if "adherent_id" in request.session:
        return RedirectResponse(url="/liver", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("homme.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["GET"])
async def login_page(request: Request):
    if "adherent_id" in request.session:
        return RedirectResponse(url="/liver", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["GET"])
async def register_page(request: Request):
    if "adherent_id" in request.session:
        return RedirectResponse(url="/liver", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("inscription.html", {"request": request})

# @app.get("/logout", response_class=HTMLResponse, tags=["GET"])
# async def logout(request: Request):

# @app.get("/api/adherents", response_model=list[Adherent])
# async def get_adherents(db: Session = Depends(get_db)):
#         adherents = db.query(Adherent).all()
#         return adherents

# @app.post("/api/register", response_model=Adherent)
# async def register_adherent(adherent: AdherentCreate, db: Session = Depends(get_db)):
#         # Vérifier si l'email existe déjà
#         db_adherent = db.query(Adherent).filter(Adherent.email == adherent.email).first()
#         if db_adherent:
#             raise HTTPException(status_code=400, detail="L'email est déjà utilisé")

#         # Créer un nouvel enregistrement
#         new_adherent = Adherent(
#             nom=adherent.nom,
#             prenom=adherent.prenom,
#             email=adherent.email
#         )

#         db.add(new_adherent)
#         db.commit()
#         db.refresh(new_adherent)

#         return {"id": adherent.id, "message": "Adhérent enregistré avec succès"}

# @app.get("/profil", response_class=HTMLResponse)
# async def profil_page(request: Request):
#     # Exemple de données fictives
#     adherent = {
#         "nom": "Dupont Jean",
#         "email": "jean.dupont@example.com",
#         "role": "Adhérent",
#         "date_inscription": "2025-08-13"
#     }
#     emprunts = [
#         {"titre": "Le Petit Prince", "date_emprunt": "2025-08-01", "date_retour": "2025-08-20", "statut": "En cours"},
#         {"titre": "1984", "date_emprunt": "2025-07-15", "date_retour": "2025-08-05", "statut": "Retourné"}
#     ]
#     return templates.TemplateResponse(
#         "profil.html",
#         {"request": request, "adherent": adherent, "emprunts": emprunts}
#     )

# @app.get("/livre/{livre_id}", response_class=HTMLResponse)
# async def livre_detail(request: Request, livre_id: int):
#     livre = {
#         "id": livre_id,
#         "titre": "Le Petit Prince",
#         "auteur": "Antoine de Saint-Exupéry",
#         "resume": "Un aviateur rencontre un petit prince venu d'une autre planète...",
#         "disponible": True,
#         "image_url": "/static/images/petitprince.jpg"
#     }
#     return templates.TemplateResponse(
#         "livre_detail.html",
#         {"request": request, "livre": livre}
#     )