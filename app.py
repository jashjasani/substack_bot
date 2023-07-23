import json
import os
import stripe
import aiohttp
import asyncio
import logging
from telegram.ext import Application
from gevent.pywsgi import WSGIServer
import uvicorn
from asgiref.wsgi import WsgiToAsgi 
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from db import addUser, findUser

load_dotenv()


STRIPE_KEY = os.getenv("STRIPE_KEY")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HTTP_LOC = os.getenv("HTTP_LOC")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# stripe api key & endpoint secret
stripe.api_key = STRIPE_KEY
endpoint_secret = STRIPE_WEBHOOK



app = Flask(__name__)



async def send_invite(channel_id,user_id):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    link = await application.bot.create_chat_invite_link(chat_id=channel_id, member_limit=1)
    await application.bot.send_message(user_id,f"Hey there, your payment was succesful\nHere's your private invite link 🔑 \n\n {link['invite_link']}" )



@app.route('/success', methods=['GET'])
def success():
    return '<html><head><link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet"></head><style>body {text-align: center; padding: 40px 0; background: #EBF0F5;} h1 {color: #88B04B; font-family: "Nunito Sans", "Helvetica Neue", sans-serif; font-weight: 900; font-size: 40px; margin-bottom: 10px;} p {color: #404F5E; font-family: "Nunito Sans", "Helvetica Neue", sans-serif; font-size:20px; margin: 0;} i {color: #9ABC66; font-size: 100px; line-height: 200px; margin-left:-15px;} .card {background: white; padding: 60px; border-radius: 4px; box-shadow: 0 2px 3px #C8D0D8; display: inline-block; margin: 0 auto;}</style><body><div class="card"><div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;"><i class="checkmark">✓</i></div><h1>Success</h1><p>We received your purchase request;<br/> You will receive an invitation shortly!</p></div></body></html>'

@app.route('/cancel', methods=['GET'])
def cancel():
    return '<html><head><style> *{transition: all 0.6s;} html {height: 100%;} body{font-family: "Lato", sans-serif; color: #888; margin: 0;} #main{display: table; width: 100%; height: 100vh; text-align: center;} .fof{display: table-cell; vertical-align: middle;} .fof h1{font-size: 50px; display: inline-block; padding-right: 12px; animation: type .5s alternate infinite;} @keyframes type{from{box-shadow: inset -3px 0px 0px #888;} to{box-shadow: inset -3px 0px 0px transparent;}}</style></head><body><div id="main"><div class="fof"><h1>Sorry to see you go</h1><h2>You know what you are missing out on?</h2></div></div></body></html>'

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
        logging.debug(event)
    except Exception as e:
        print('⚠️ Webhook error while parsing basic request.', str(e))
        return jsonify(success=False)

    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except stripe.error.SignatureVerificationError as e:
            print('⚠️ Webhook signature verification failed.', str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'checkout.session.completed':
        user_id = event['data']['object']['metadata']['user_id']
        username = event['data']['object']['metadata']['username']
        name = event['data']['object']['metadata']['name']
        subscription_type = event['data']['object']['metadata']['type']
        type = event['data']['object']['metadata']['type']
        email = event['data']['object']['customer_details']['email']
        channel_id = event['data']['object']['metadata']['channel_id']
        start_date = datetime.now().date()
        if subscription_type == "M":
            end_date = (datetime.now() + timedelta(days=30)).date()
        elif subscription_type == "L":
            end_date = (datetime.now() + timedelta(days=365*99)).date()
        if not findUser(COLLECTION_NAME, user_id=user_id):
            data = {
                "user_id": user_id,
                "username": username,
                "type": type,
                "channel_id": channel_id,
                "email": email,
                "start_date": start_date,
                "end_date": end_date
            }
            print(data)
            data = {k: v for k, v in data.items() if v is not None}
            addUser(data=data)
            asyncio.run(send_invite(channel_id,user_id))
    elif event['type'] == '.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

def main():
    asgi_app = WsgiToAsgi(app.wsgi_app)

   
    uvicorn.run(asgi_app, host='0.0.0.0', port=80)

    

if __name__ == "__main__":
    main()
