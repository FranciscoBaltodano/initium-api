import json
import logging
from fastapi import HTTPException
from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_card(query: str, is_fetching=True):
    try:
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result = json.loads(result_json)

        if not is_fetching:
            result = result[0]
            if result.get("status") == 404:
                raise HTTPException(status_code=404, detail="Card not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

async def get_cards():
    query = "EXEC initium.get_cards"
    result_dict = await fetch_card(query)
    return result_dict

async def get_card(id: int):
    query = f"EXEC initium.get_card_by_id @id = {id}"
    result_dict = await fetch_card(query)
    if not result_dict:
        raise HTTPException(status_code=404, detail="Card not found")
    return result_dict[0]

async def delete_card(id: int):
    query = f"EXEC initium.delete_card @card_id = {id};"
    result_dict = await fetch_card(query, is_fetching=False)
    return result_dict

async def update_card(id: int, title: str, description: str):
    query = f"EXEC initium.update_card @id = {id}, @title = '{title}', @description = '{description}';"
    result_dict = await fetch_card(query, is_fetching=False)
    return result_dict

async def create_card(title: str, description:str):
    query = f"EXEC initium.create_card @title = '{title}', @description = '{description}';"
    result_dict = await fetch_card(query, is_fetching=False)
    return result_dict