from fastapi import APIRouter, Response
from models.Card import Card
from controllers.card import get_cards, get_card, delete_card, update_card, create_card

router = APIRouter()

@router.get("/cards")
async def all_cards(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await get_cards()

@router.post("/cards")
async def new_cards(response: Response, card: Card):
    response.headers["Cache-Control"] = "no-cache"
    return await create_card(card.title, card.description)

@router.get("/cards/{card_id}")
async def get_card_by_id(card_id: int, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await get_card(card_id)

@router.delete("/cards/{card_id}")
async def card_delete(card_id: int, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await delete_card(card_id)

@router.put("/cards/{card_id}")
async def card_update(card_id: int, response: Response, card: Card):
    response.headers["Cache-Control"] = "no-cache"
    return await update_card(card_id, card.title, card.description)
