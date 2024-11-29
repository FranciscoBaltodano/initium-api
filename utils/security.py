import os
import secrets
import hashlib
import base64
import jwt

import secrets
import hashlib
import base64

from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_FUNC = os.getenv("SECRET_KEY_FUNC")

def create_jwt_token(firstname:str, lastname:str, email: str, active: bool):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "active": active,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

def validate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")


        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid authentication scheme")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


            email = payload.get("email")
            expired = payload.get("exp")
            active = payload.get("active")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")



            if email is None or expired is None or active is None:
                raise HTTPException(status_code=400, detail="Invalid token")

            if datetime.utcfromtimestamp(expired) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            if not active:
                raise HTTPException(status_code=403, detail="Inactive user")

            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired token")

        return await func(*args, **kwargs)
    return wrapper

def validate_for_inactive(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            token = authorization.split()[1]

            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            expired = payload.get("exp")

            if email is None or expired is None:
                raise HTTPException(status_code=422, detail="Missing required fields")

            if datetime.utcfromtimestamp(expired) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            request.state.email = email
        except PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token or expired token")
        return await func(*args, **kwargs)
    return wrapper


def validate_func(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=403, detail="Authorization header missing")

        if authorization != SECRET_KEY_FUNC:
            raise HTTPException(status_code=403, detail="Wrong function key")

        return await func(*args, **kwargs)
    return wrapper