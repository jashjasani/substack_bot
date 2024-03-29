import logging
from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton
from telegram.ext import Updater, Application, CallbackQueryHandler, CommandHandler, ContextTypes
import stripe
import json
import os
from flask import Flask, jsonify, request
import aiohttp
import asyncio
from telegram.constants import ParseMode
from datetime import datetime 
import os
from dotenv import load_dotenv
from db import findUser


load_dotenv()


STRIPE_KEY = os.getenv("STRIPE_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HTTP_LOC = os.getenv("HTTP_LOC")

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


stripe.api_key = STRIPE_KEY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("250 monthly", callback_data="1")
        ],
        [
            InlineKeyboardButton("1500 lifetime", callback_data="2")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.message

    await update.message.reply_text(text=f"Hello {user.from_user.first_name}")
    await update.message.reply_text(text="<strong>Sam & Adah</strong> \n\nYour favourite reddit couple's \npremiuim channel \n\nPlease select your subscription plan:", reply_markup=reply_markup,parse_mode=ParseMode.HTML)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    await query.answer()

    if query.data == "1":
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',  # Replace with the appropriate currency
                        'unit_amount': 25000,  # Price amount in cents
                        'product_data': {
                            'name': '1 month subscription',
                            'description': 'Full access to channel for 1 month',
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                        "user_id": query.from_user.id,
                        "username": query.from_user.username,
                        "name" : query.from_user.full_name,
                        "date" : datetime.now().date().strftime("%d-%m-%Y"),
                        "type" : "M",
                        "channel_id" : CHANNEL_ID
                    },
            mode='payment',
            success_url=f"http://{HTTP_LOC}/success",
            cancel_url=f"http://{HTTP_LOC}/cancel",

        )
        url = session["url"]
        keyboard = [
            [
                InlineKeyboardButton(text="Payment Link", url=url)
            ],
            [
                InlineKeyboardButton(text="<< Back", callback_data="back_to_start")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the shortened text message with the inline keyboard
        await query.message.edit_text("<strong>Monthly Plan</strong>\n\nYour benefits:\n&#9989; Sam &amp; Adah (Access to the channel)\n\nPrice: ₹250.00\nBilling period: 1 month\nBilling mode: one-time",parse_mode=ParseMode.HTML)
        await query.message.reply_text("Complete payment in below link 👇", reply_markup=reply_markup)
    elif query.data == "2":
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',  # Replace with the appropriate currency
                        'unit_amount': 150000,  # Price amount in cents
                        'product_data': {
                            'name': 'Life-time subscription',
                            'description': 'Lifetime membership',
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                        "user_id": query.from_user.id,
                        "username": query.from_user.username,
                        "name" : query.from_user.full_name,
                        "type" : "L",
                        "channel_id" : CHANNEL_ID
                    },
            mode='payment',
            success_url=f"http://{HTTP_LOC}/success",
            cancel_url=f"http://{HTTP_LOC}/cancel",

        )
        url = session["url"]
        keyboard = [
            [
                InlineKeyboardButton(text="Payment Link", url=url)
            ],
            [
                InlineKeyboardButton(text="<< Back", callback_data="back_to_start")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the shortened text message with the inline keyboard
        await query.message.edit_text("<strong>Monthly Plan</strong>\n\nYour benefits:\n&#9989; Sam &amp; Adah (Access to the channel)\n\nPrice: ₹1500.00\nBilling period: lifetime",parse_mode=ParseMode.HTML)
        await query.message.reply_text("Complete payment in below link 👇", reply_markup=reply_markup)
    elif query.data =="back_to_start":
        keyboard = [
            [
                InlineKeyboardButton("250 monthly", callback_data="1")
            ],
            [
                InlineKeyboardButton("1500 lifetime", callback_data="2")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text="<strong>Sam & Adah</strong> \n\nYour favourite reddit couple's \npremiuim channel \n\nPlease select your subscription plan:", reply_markup=reply_markup,parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = findUser("user",user_id=user_id)
    if user:
        type = user["type"]
        end_date = user["end_date"]
        if type == "M":
            await update.message.reply_text(f"You are subscribed to monthly plan ✅\nYour current plan is ending on : {end_date}")
        elif type == "L":
            await update.message.reply_text(f"Yayyy!!! you are subscribed to lifetime plan ✅")
    else:
        await update.message.reply_text(f"No active subscriptions ❌")


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
   

if __name__ == "__main__":
    main()
