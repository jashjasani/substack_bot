from sendMessage import auth_invite,create_join_link
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
stripe.api_key = "sk_test_51MxG33SA2e71Dz91F5a9eLJOANuxRy6lYhBgRb84yoPwlmotLGwLbBAx7QO4G13htPcK7d1Sv3dgYrjKYicyTajv00NYpBtLbw"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
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
    await update.message.reply_text(text="Sam & Adah \n\nYour favourite reddit couple's \npremiuim channel \n\nPlease select your subscription plan:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    print(query.from_user.id)

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
                        "date" : datetime.now().date
                    },
            mode='payment',
            success_url="https://google.com/cancel",
            cancel_url="https://google.com/cancel",

        )
        url = session["url"]
        button = InlineKeyboardButton(text="Link", url=url)
        reply_markup = InlineKeyboardMarkup([[button]])
        # Send the shortened text message with the inline keyboard
        await query.message.edit_text("<strong>Monthly Plan</strong>\n\nYour benefits:\n&#9989; Sam &amp; Adah (Access to the channel)\n\nPrice: ₹250.00\nBilling period: 1 month\nBilling mode: recurring",parse_mode=ParseMode.HTML)
        await query.message.reply_text("Complete payment in below link", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        "6240244195:AAGfzgpe-mRWR9xru-zq2QaFu5QjPvx_Ugc").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    #! /usr/bin/env python3.6


if __name__ == "__main__":
    main()
