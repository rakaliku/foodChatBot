# Food Order Dialogflow Chatbot

This repository contains the code for a food order chatbot built using Dialogflow and Python. The bot supports the following functionalities:

1. **New Order**: Allows users to place a new food order.
2. **Track Order**: Enables users to track the status of their existing order.

The webhook for this chatbot is deployed using **ngrok** to provide a public URL for Dialogflow's fulfillment.

---

## Features

### 1. **New Order**
- Users can browse the menu and place a new order.
- The chatbot captures user details like name, address, and contact information.
- It provides a confirmation of the order placed.

### 2. **Track Order**
- Users can check the status of their existing orders by providing their order ID.
- The bot retrieves the order status and responds with the current stage (e.g., "Preparing", "Out for Delivery", "Delivered").

---

## Prerequisites

Before you begin, ensure you have the following installed:

1. Python 3.7 or above
2. Dialogflow account
3. ngrok (for exposing the webhook)
4. Required Python libraries (listed in `requirements.txt`)

---

## Setup Instructions

### 1. Clone the Repository
```bash
$ git clone https://github.com/rakaliku/foodChatBot.git
$ cd foodChatBot
```

### 2. Install Dependencies
Install the required Python libraries using the following command:
```bash
$ pip install -r requirements.txt
```

### 3. Dialogflow Setup
- Create a new agent in Dialogflow.
- Import the `intents` and `entities` provided in the `dialogflow_resources/` folder to your agent.
- Navigate to the **Fulfillment** section in Dialogflow and enable the webhook.
- Paste the ngrok-generated URL (explained below) in the **Webhook URL** field.

### 4. ngrok Setup
- Download and install ngrok from [https://ngrok.com/](https://ngrok.com/).
- Run the following command in the project directory where the ngrok exe file is present to start ngrok and expose your local server:
```bash
$ ngrok http 8000
```
- Copy the generated public URL (e.g., `https://xyz.ngrok.app`) and update it as the webhook URL in Dialogflow.

### 5. Run the Fast API Server
Start the Fast API server to handle webhook requests from Dialogflow:
```bash
$  uvicorn main:app --reload    
```

---

## File Structure

```
food-order-dialogflow-bot/
|├── main.py                # Main Fast API application for handling webhook requests
|├── requirements.txt     # Python dependencies
|├── dialogflow_assets # Required intent and entites details mentioned
|├── README.md           # Project documentation (this file)
|├── db                  # Required SQL file to run the project
```

---

## How It Works

### Webhook
- The `main.py` file defines a Fast API application that listens for POST requests from Dialogflow.
- The `new_order` and `track_order` functionalities are handled based on the intent detected in the incoming request.

### ngrok
- ngrok exposes the local Fast API server to the internet, making it accessible to Dialogflow.

---

## Example Usage

### New Order
1. User: "I want to order a pizza."
2. Bot: "Sure, please provide your address."
3. User: "123 Main Street."
4. Bot: "Thank you! Your order has been placed."

### Track Order
1. User: "Where's my order?"
2. Bot: "Please provide your order ID."
3. User: "12345."
4. Bot: "Your order is currently out for delivery."

---

## Notes
- Ensure ngrok is running whenever you are testing the chatbot.
- Use a persistent database if required for storing order details.

---

## Troubleshooting

1. **Webhook URL Not Working**
   - Verify ngrok is running and the public URL is correct.
   - Check if the Fast API server is running.

2. **Dialogflow Intents Not Triggering**
   - Ensure the intents and entities are imported correctly into your Dialogflow agent.
   - Verify the webhook is enabled and the URL is set correctly.



