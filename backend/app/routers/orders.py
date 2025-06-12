from fastapi import APIRouter, HTTPException
from typing import List
from ..models.order import Order
from ..database import db
from bson import ObjectId

router = APIRouter(prefix="/orders", tags=["Órdenes"])

def order_helper(order) -> dict:
    order["id"] = str(order["_id"])
    del order["_id"]
    return order

@router.post("/", response_model=Order)
async def create_order(order: Order):
    result = await db.orders.insert_one(order.dict(exclude={"id"}))
    order.id = str(result.inserted_id)
    return order

@router.get("/", response_model=List[Order])
async def get_orders():
    orders = await db.orders.find().to_list(100)
    return [order_helper(o) for o in orders]
