import os
import requests
import json
import logging
import traceback
import random
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException

from models.UserRegister import UserRegister
from models.UserLogin import UserLogin
from models.EmailActivation import EmailActivation
from models.UserActivation import UserActivation

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from utils.database import fetch_query_as_json
from utils.security import create_jwt_token

from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cred = credentials.Certificate("secrets/firebase-adminsdk.json")
firebase_admin.initialize_app(cred)


load_dotenv()


azure_sak = os.getenv('AZURE_SAK')
queue_name = os.getenv('QUEUE_ACTIVATE')


queue_client = QueueClient.from_connection_string(azure_sak, queue_name)
queue_client.message_decode_policy = BinaryBase64DecodePolicy()
queue_client.message_encode_policy = BinaryBase64EncodePolicy()

async def insert_message_on_queue(message: str):
    try:
        message_bytes = message.encode('utf-8')
        queue_client.send_message(
            queue_client.message_encode_policy.encode(message_bytes)
        )
        logger.info(f"Message inserted in queue: {message}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise


async def register_user_firebase(user: UserRegister):
    user_record = {}
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="This email is already registered")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")

    query = f" exec initium.create_user @email = '{user.email}', @firstname = '{user.firstname}', @lastname = '{user.lastname}'"
    result = {}
    try:

        result_json = await fetch_query_as_json(query, is_procedure=True)
        result = json.loads(result_json)[0]

        await insert_message_on_queue(user.email)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def login_user_firebase(user: UserLogin):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")  
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(status_code=401, detail=f"Error authenticating user: {response_data['error']['message']}")

        query = f"""select email, firstname, lastname, active
                    from [initium].[users]
                    where email = '{ user.email }'
                """
        try:
            result_json = await fetch_query_as_json(query)
            result_dict = json.loads(result_json)
            return {
                "message": "User authenticated successfully",
                "idToken": create_jwt_token(
                    result_dict[0]["firstname"],
                    result_dict[0]["lastname"],
                    result_dict[0]["email"],
                    result_dict[0]["active"]
                )
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(
            status_code=400,
            detail=f"Error login user: {error_detail}"
        )

async def generate_activation_code(email: EmailActivation):
    code = random.randint(100000, 999999)
    
    query = f" exec initium.generate_activation_code @email = '{email.email}', @code = {code}"
    try:
        await fetch_query_as_json(query, is_procedure=True)
        return {"message": "Activation code generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating activation code: {e}")

async def activate_user(user: UserActivation):
    query = f"""
            select email, case when GETDATE() between created_at and expired_at then 'active'
            else 'expired' end as status
            from initium.activation_codes
            where email = '{user.email}' and code = {user.code}
            """
    try:
        result_json = await fetch_query_as_json(query)

        if result_json == "[]":
            raise HTTPException(status_code=404, detail="Activation code not found")
        
        result_dict = json.loads(result_json)[0]

        if result_dict["status"] == "expired":
            await insert_message_on_queue(user.email)
            raise HTTPException(status_code=400, detail="Code expired, we send a new one")
        query=f"EXEC initium.activate_user @email = '{user.email}'"

        result_json = await fetch_query_as_json(query, is_procedure=True)
        return{"message": "User activated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error activating user: {e}')
    


async def get_user_by_email(email: str):
    try:
        # Llamar al procedimiento almacenado para obtener el usuario por email
        query = f"EXEC GetUserByEmail @email = '{email}'"
        result_json = await fetch_query_as_json(query)

        print(f"Result from query: {result_json}")  # Verifica el resultado de la consulta
        if result_json == "[]":
            raise HTTPException(status_code=404, detail="Activation code not found")
        
        result_dict = json.loads(result_json)[0]
        # Devuelve los datos del usuario
        return result_dict  # Tomar el primer (y único) resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
