import json
import os
import stripe
import aiohttp
from sendMessage import auth_invite
# This is a public sample test API key.
# Don’t submit any personally identifiable information in requests made with this key.
# Sign in to see your own test API key embedded in code samples.
stripe.api_key = 'sk_test_51MxG33SA2e71Dz91F5a9eLJOANuxRy6lYhBgRb84yoPwlmotLGwLbBAx7QO4G13htPcK7d1Sv3dgYrjKYicyTajv00NYpBtLbw'

# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks
endpoint_secret = 'we_1NWCcKSA2e71Dz91vcC03C7X'
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/success',methods=['GET'])
def success():
    return '<html><head><link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet"></head><style>body {text-align: center; padding: 40px 0; background: #EBF0F5;} h1 {color: #88B04B; font-family: "Nunito Sans", "Helvetica Neue", sans-serif; font-weight: 900; font-size: 40px; margin-bottom: 10px;} p {color: #404F5E; font-family: "Nunito Sans", "Helvetica Neue", sans-serif; font-size:20px; margin: 0;} i {color: #9ABC66; font-size: 100px; line-height: 200px; margin-left:-15px;} .card {background: white; padding: 60px; border-radius: 4px; box-shadow: 0 2px 3px #C8D0D8; display: inline-block; margin: 0 auto;}</style><body><div class="card"><div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;"><i class="checkmark">✓</i></div><h1>Success</h1><p>We received your purchase request;<br/> You will receive invitation shortly!</p></div></body></html>'


@app.route('/cancel',methods=['GET'])
def cancel():
    return '<html><head><style> *{transition: all 0.6s;} html {height: 100%;} body{font-family: "Lato", sans-serif; color: #888; margin: 0;} #main{display: table; width: 100%; height: 100vh; text-align: center;} .fof{display: table-cell; vertical-align: middle;} .fof h1{font-size: 50px; display: inline-block; padding-right: 12px; animation: type .5s alternate infinite;} @keyframes type{from{box-shadow: inset -3px 0px 0px #888;} to{box-shadow: inset -3px 0px 0px transparent;}}</style></head><body><div id="main"><div class="fof"><h1>Sorry to see you go</h1><h2>You know what you are missing out on ?</h2></div></div></body></html>'


@app.route('/webhook', methods=['POST'])
async def webhook():
    
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
        print(event)
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'checkout.session.completed':
        metadata = event["metadata"]
        user_id = metadata["user_id"]
        username = metadata["username"]
        type = metadata["monthly"]
        await auth_invite(user_id=user_id)
        print('Payment for {} subscription for username : {} succeeded'.format(type,user_id))
        
    elif event['type'] == '.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)