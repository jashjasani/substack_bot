import aiohttp
import asyncio

TOKEN  = "6240244195:AAGfzgpe-mRWR9xru-zq2QaFu5QjPvx_Ugc"

url = f"https://api.telegram.org/bot{TOKEN}/"

async def send_message(chat_id, text):
    send_url = f"{url}sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(send_url, data=data) as response:
            # Handle the response if needed
            print(await response.json())


async def create_join_link(channel_id):
    create_url = f"{url}createChatInviteLink"
    data = {
        "chat_id" : channel_id,
        "member_limit" : 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(create_url, data=data) as response:
            return (await response.json())

async def auth_invite(user_id,channel_id):
    chat_id = user_id
    channel_id = channel_id
    invite_link = (await create_join_link(channel_id))["result"]["invite_link"]

    message_text = f"Your payment was succesful ✅\nHere is your one time invite link: \n{invite_link}"
    
    await send_message(chat_id, message_text)


if __name__ == "__main__":
    asyncio.run(auth_invite())
