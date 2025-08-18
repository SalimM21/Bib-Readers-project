from datetime import datetime
from fastapi import Depends, FastAPI, Form, HTTPException, Request,Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth.jwt_handler import create_access_token
from database import SessionLocal, engine, Base
from models import Adherent, Livre, Emprunt, Reservation
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import models


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")

# Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Pages HTML
# -----------------------------
@app.get("/register")
def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login")
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/")
def show_home(request: Request, db: Session = Depends(get_db)):
    livres = db.query(Livre).all()
    return templates.TemplateResponse("home.html", {"request": request, "livres": livres})


# -----------------------------
# Routes API
# -----------------------------
@app.post("/api/register")
def register_adherent(
    nom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Vérifier si l'email existe déjà
    existing_user = db.query(Adherent).filter(Adherent.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed_password = pwd_context.hash(password)
    adherent = Adherent(nom=nom, email=email, password_hash=hashed_password)
    db.add(adherent)
    db.commit()
    db.refresh(adherent)
    return RedirectResponse(url="/login", status_code=302)


@app.post("/api/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
   # Vérifier l'utilisateur
    user = db.query(Adherent).filter(Adherent.email == email).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Identifiants incorrects")

    # Générer le token JWT
    token = create_access_token({"user_id": user.id, "role": user.role})

    # Redirection vers /home après connexion
    response = RedirectResponse(url="/home", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


#-------------------------------------------------Route API pour récupérer les livres (avec recherche)--------------------------------------------

@app.get("/api/livres")
def get_livres(search: str = Query(default=""), db: Session = Depends(get_db)):
    query = db.query(Livre)
    if search:
        query = query.filter(Livre.title.ilike(f"%{search}%"))
    livres = query.all()

    # Retourne les livres en JSON
    return [
        {
            "id": livre.id,
            "title": livre.title,
            "description": livre.description,
            "price": float(livre.price) if livre.price else None,
            "availability": livre.availability,
            "availability_num": livre.availability_num,
            "image_url": livre.image_url,
            "rating": livre.rating
        }
        for livre in livres
    ]


#------------------------------------------Route FastAPI pour la page catalogue--------------------------------------


PER_PAGE = 20  # livres par page

@app.get("/catalogue", response_class=HTMLResponse)
def catalogue(request: Request, page: int = 1, search: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Livre)
    if search:
        query = query.filter(models.Livre.title.ilike(f"%{search}%"))
    
    total_livres = query.count()
    total_pages = (total_livres + PER_PAGE - 1) // PER_PAGE

    livres = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()

    return templates.TemplateResponse(
        "catalogue.html",
        {
            "request": request,
            "livres": livres,
            "search": search,
            "page": page,
            "total_pages": total_pages
        }
    )

@app.get("/reserver/{livre_id}")
def reserver(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    if livre.availability_num > 0:
        livre.availability_num -= 1
        if livre.availability_num == 0:
            livre.availability = "réservé"
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="Livre déjà réservé")
    return RedirectResponse(url=f"/reservations", status_code=302)

#----------------------------------------------Route pour afficher les détails d'un livre---------------------------------------
@app.get("/livre/{livre_id}", response_class=HTMLResponse)
def lire_livre(request: Request, livre_id: int, db: Session = Depends(get_db)):
    # Récupérer le livre depuis la base
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    # Retourner le template livre.html avec le livre
    return templates.TemplateResponse("livre.html", {"request": request, "livre": livre})
#--------------------------------------------------resever livre
@app.post("/reserver/{livre_id}")
def reserver_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    if not livre:
        # Redirection avec paramètre error
        return RedirectResponse(url=f"/livre/{livre_id}?error=notfound", status_code=303)
    
    if not livre.availability:
        # Livre déjà réservé
        return RedirectResponse(url=f"/livre/{livre_id}?error=reserved", status_code=303)
    
    # Réservation réussie
    livre.availability = False
    db.commit()
    return RedirectResponse(url=f"/livre/{livre_id}?success=1", status_code=303)

#----------------------------------------------Route pour afficher les réservations d'un utilisateur---------------------------------------

@app.get("/reservations")
def reservations(request: Request, db: Session = Depends(get_db)):
    # Récupérer tous les livres qui ont été réservés (availability_num == 0)
    livres_reserves = db.query(models.Livre).filter(models.Livre.availability_num == 0).all()
    return templates.TemplateResponse("reservations.html", {"request": request, "livres": livres_reserves})
#------------------------------------------------Route de reservation ----------------------------------

from fastapi import Request

def get_current_adherent(request: Request, db: Session = Depends(get_db)):
    # Récupérer l'email de l'adhérent depuis la session (ou cookie)
    email = request.session.get("user_email")  # ex : stocké lors du login
    if not email:
        raise HTTPException(status_code=401, detail="Adhérent non authentifié")
    adherent = db.query(Adherent).filter(Adherent.email == email).first()
    if not adherent:
        raise HTTPException(status_code=401, detail="Adhérent non trouvé")
    return adherent

@app.post("/api/reservations")
def reserver_livre(
    livre_id: int = Form(...),
    db: Session = Depends(get_db),
    current_adherent: Adherent = Depends(get_current_adherent)
):
    # Vérifier que le livre existe
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    if not livre:
        return RedirectResponse(url="/?error=notfound", status_code=303)

    # Vérifier disponibilité
    if not livre.availability:
        return RedirectResponse(url="/?error=reserved", status_code=303)

    # Vérifier si déjà réservé
    existing_reservation = db.query(Reservation).filter(
        Reservation.adherent_id == current_adherent.id,
        Reservation.livre_id == livre_id
    ).first()
    if existing_reservation:
        return RedirectResponse(url="/?error=alreadyreserved", status_code=303)

    # Créer réservation
    reservation = Reservation(
        adherent_id=current_adherent.id,
        livre_id=livre_id,
        date_reservation=datetime.utcnow()
    )
    db.add(reservation)

    # Mettre à jour disponibilité
    livre.availability = False
    db.commit()

    # Rediriger avec succès
    return RedirectResponse(url="/?success=1", status_code=303)







#----------------------------------------------Route FastAPI pour la page de recommandations---------------------------------------
'''
from recommendation import get_recommendations, recommend_by_description

@app.get("/recommandations", response_class=HTMLResponse)
def recommandations(request: Request, livre: str = Query(default=None)):
    recommandations = []
    if livre:
        recommandations = get_recommendations(livre, top_n=6)
    
    # Afficher la page HTML
    return templates.TemplateResponse(
        "recommandations.html",
        {"request": request, "recommandations": recommandations, "livre": livre}
    )
@app.get("/recommandations", response_class=HTMLResponse)
def show_recommendations_page(request: Request):
    """
    Affiche la page HTML de recommandations avec un formulaire pour saisir
    un titre ou une description
    """
    return templates.TemplateResponse("recommandations.html", {"request": request, "livres": []})

@app.post("/recommandations", response_class=HTMLResponse)
def recommend_books(request: Request, title: str = Form(None), description: str = Form(None)):
    """
    Traite le formulaire de recommandations
    """
    livres = []

    if title:
        livres = get_recommendations(title, top_n=5)
    elif description:
        livres = recommend_by_description(description, top_n=5)

    return templates.TemplateResponse(
        "recommandations.html",
        {"request": request, "livres": livres, "input_title": title, "input_description": description}
    )'''
