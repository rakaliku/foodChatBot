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
    print("handler request......")
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        print(f"intent is {intent}")
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id = generic_helper.extract_session(output_contexts[0]["name"])
        print(f"session id is {session_id}")
        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            # 'order.remove - context: ongoing order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context : ongoing tracking': track_order
        }
        if intent in intent_handler_dict:
            print(f"intent is if block {intent}")
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

    # if intent == "track.order - context : ongoing tracking":
    #     print(intent)
    #     return track_order(parameters)


def add_to_order(parameters: dict, session_id: str):
    print(" add to order function started........")
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

        print("*********************")
        print(inprogress_order)
        order_str = generic_helper.get_str_from_food_dict(inprogress_order[session_id])
        print("order placed.........")
        fulfillmentText = f"so far you ordered : {order_str}. Do you need anything else?"

    return JSONResponse(content=
        {"fulfillmentText": fulfillmentText}
    )


def remove_from_order(parameters: dict):
    pass

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillmentText = " I'm sorry did not get your order no..."
    else:
        order = inprogress_order[session_id]
    return  JSONResponse(
        content={
            "fulfillmentText": "thanks for your orders, its in progress"
        }
    )


# def save_to_db(order: dict)

def track_order(parameters: dict):
    print("track Order function started....")
    # order_id = int(parameters.get('order_id', None))
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