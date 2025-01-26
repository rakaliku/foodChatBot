from typing import Union

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

import db_helper
import generic_helper

app = FastAPI()

inprogress_order = {}

@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id = generic_helper.extract_session(output_contexts[0]["name"])
        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context : ongoing tracking': track_order
        }
        if intent in intent_handler_dict:
            return intent_handler_dict[intent](parameters, session_id)
        else:
            return JSONResponse(content={"fulfillmentText":f"Unhandled Intent {intent}"})

    except Exception as e:
        print(f"Error in webhook processing {e}")
        return JSONResponse(
            content={
                "fulfillmentText": f"Error in webhook processing {str(e)}"
            }
        )


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillmentText = "Sorry, please specify the quantities of food properly"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_order:
            current_food_dict = inprogress_order[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_order[session_id] = current_food_dict
        else:
            inprogress_order[session_id] = new_food_dict
        order_str = generic_helper.get_str_from_food_dict(inprogress_order[session_id])
        fulfillmentText = f"so far you ordered : {order_str}. Do you need anything else?"

    return JSONResponse(content=
        {"fulfillmentText": fulfillmentText}
    )


def remove_from_order(parameters: dict, session_id: str):

    if session_id not in inprogress_order:
        return JSONResponse(content=
                            {
                                "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"}
                            )
    food_items = parameters["food-item"]
    current_order = inprogress_order[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillmentText = " I'm sorry did not get your order no..."
    else:
        order = inprogress_order[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillmentText = "Sorry could not place your order due to backend error" \
                                "Please place new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillmentText = f"Awesome..Order is placed ..order id is -{order_id} and total order is - {order_total}"


        del inprogress_order[session_id]
    return  JSONResponse(
        content={
            "fulfillmentText": fulfillmentText
        }
    )


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return  -1

    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id

def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    if not order_id:
        return JSONResponse(
            content={"fulfillmentText": "Invalid request: Missing 'order_id' parameter"}
        )

    try:
        order_status = db_helper.get_order_status(order_id)
    except Exception as e:
        print(f"Database error: {e}")
        return JSONResponse(
            content={"fulfillmentText": "There was an error fetching order status. Please try again later."}
        )

    if order_status:
        fulfillmentText = f"order id is {order_id} and status is : {order_status}"
    else:
        fulfillmentText = f"no order found for order id {order_id}"
    return JSONResponse(
        content={
            "fulfillmentText": fulfillmentText
        }
    )