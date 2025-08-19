
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Query
from recommendation import recommend, recommend_by_description


app = FastAPI()

@app.get("/api/recommender/{book_id}")
def recommender(book_id: int):
    recommendations = recommend(book_id)
    return JSONResponse(content={"recommandations": recommendations})



@app.get("/api/recommender-by-description")
def recommender_desc(description: str = Query(..., min_length=5)):
    recommendations = recommend_by_description(description)
    return JSONResponse(content={"recommandations": recommendations})
