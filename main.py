import json
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Response
from utils.database import fetch_query_as_json

from routers import cards, users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(cards.router, tags=["cards"])
app.include_router(users.router, tags=["users"])

@app.get("/")
async def read_root(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    query = "select * from initium.notes"
    try:
        result = await fetch_query_as_json(query)
        result_dict = json.loads(result)
        result_dict = {
            "data": result_dict
            , "version": "0.0.1"
        }
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)