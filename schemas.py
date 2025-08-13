from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, engine

from database import Base

class AdherentCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr

class Adherent(AdherentCreate):
    id: int
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class Livre(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[int] = None
    availability_num: Optional[int] = None

    class Config:
        orm_mode = True


    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_reservation = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default="en_attente")  # en_attente / disponible / annulee

# class LivreCreate(BaseModel):
#     title: str
#     description: Optional[str] = None
#     price: Optional[float] = None
#     availability: Optional[str] = None
#     image_url: Optional[str] = None
#     rating: Optional[int] = None
#     availability_num: Optional[int] = None

#     class Config:
#         orm_mode = True 
#         allow_population_by_field_name = True
#         use_enum_values = True
#         json_encoders = {
#             datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
#         }
#         schema_extra = {
#             "example": {
#                 "title": "Example Book",
#                 "description": "This is an example book description.",  
#                 "price": 19.99,
#                 "availability": "In Stock",
#                 "image_url": "http://example.com/image.jpg",
#                 "rating": 5,
#                 "availability_num": 10
#             }
#         }
# class LivreUpdate(BaseModel):
    # title: Optional[str] = None
    # description: Optional[str] = None
    # price: Optional[float] = None
    # availability: Optional[str] = None
    # image_url: Optional[str] = None
    # rating: Optional[int] = None
    # availability_num: Optional[int] = None
    # class Config:
    #     orm_mode = True
    #     allow_population_by_field_name = True
    #     use_enum_values = True
    #     json_encoders = {
    #         datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v 
    #     }
    #     schema_extra = {
    #         "example": {
    #             "title": "Updated Book Title",
    #             "description": "Updated description for the book.",
    #             "price": 24.99,
    #             "availability": "Out of Stock",
    #             "image_url": "http://example.com/updated_image.jpg",
    #             "rating": 4,
    #             "availability_num": 0
    #         }
    #     }

