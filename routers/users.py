from fastapi import APIRouter, Response, Request

from utils.security import validate, validate_func, validate_for_inactive
from fastapi.responses import JSONResponse
from models.UserActivation import UserActivation
from models.UserRegister import UserRegister
from models.UserLogin import UserLogin
from models.EmailActivation import EmailActivation

from controllers.firebase import register_user_firebase, login_user_firebase, generate_activation_code, activate_user, get_user_by_email

router = APIRouter()

@router.post("/register")
async def register_user(user: UserRegister):
    return  await register_user_firebase(user)

@router.post("/login")
async def login(user: UserLogin):
    return await login_user_firebase(user)


@router.get("/user")
@validate
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache"

    user_data = await get_user_by_email(request.state.email)
    return JSONResponse(content=user_data) 

@router.post("/user/{email}/code")
@validate_func
async def send_activation_code(email: str, request: Request):
    e = EmailActivation(email=email)
    return await generate_activation_code(e)

@router.put("/user/code/{code}")
@validate_for_inactive
async def activate_user_by_code(request: Request, code: str):
    user = UserActivation(email=request.state.email, code=code)
    return await activate_user(user)

