# import json
# import uvicorn
# from typing import Union
# from pydantic import BaseModel

# from fastapi import FastAPI, HTTPException

# from utils.database import fetch_query_as_json
# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_credentials=True
# )

# @app.get("/")
# async def read_root():
#     query = "select * from initium.notes"
#     try:
#         result = await fetch_query_as_json(query)
#         result_dict = json.loads(result)
#         return { "data": result_dict, "version": "0.0.0" }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# # class Item(BaseModel):
# #     name: str
# #     price: float
# #     is_offer: Union[bool, None] = None


# # @app.get("/")
# # async def read_root():
# #     return {"Hello": "World"}

# # @app.put("/items/{item_id}")
# # def update_item(item_id: int, item: Item):
# #     return {"item_name": item.name, "item_id": item_id}

# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000)

































import json
import uvicorn

from typing import Union
from fastapi import FastAPI, HTTPException, Response, Request
from utils.database import fetch_query_as_json
from utils.security import validate, validate_func

from fastapi.middleware.cors import CORSMiddleware
from models.UserRegister import UserRegister
from models.UserLogin import UserLogin
from models.EmailActivation import EmailActivation

from controllers.firebase import register_user_firebase, login_user_firebase, generate_activation_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
async def read_root(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    query = "select * from initium.notes"
    try:
        result = await fetch_query_as_json(query)
        result_dict = json.loads(result)
        result_dict = {
            "data": result_dict
            , "version": "0.0.0"
        }
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/register")
async def register(user: UserRegister):
    return  await register_user_firebase(user)

@app.post("/login")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache";
    return {
        "email": request.state.email
        , "firstname": request.state.firstname
        , "lastname": request.state.lastname
    }

@app.post("/user/{email}/code")
@validate_func
async def generate_code(request: Request, email: str):
    e = EmailActivation(email=email)
    return await generate_activation_code(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)