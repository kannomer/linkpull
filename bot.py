import logging
import os
from dotenv import load_dotenv
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import aiohttp
from urllib.parse import urlparse
import aiofiles
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

startMessage = "Hello. Send me a link for me to download. Example: example.com/example.zip"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=startMessage) # type: ignore

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't understand that command.") # type: ignore

def get_filename_from_url(url: str):
    path = urlparse(url).path
    name = os.path.basename(path)
    return name or "downloaded_file"

async def grabLink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url: str = update.message.text # type: ignore
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Download started...") # type: ignore
    startTime = time.time()

    timeout = aiohttp.ClientTimeout(total=None, sock_connect=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, allow_redirects=True) as resp:

            resp.raise_for_status()

            contentType = resp.headers.get("Content-Type", "")
            if "text/html" in contentType:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, # type: ignore
                    text="Make sure the link is a direct file download."
                )
                return

            filename = get_filename_from_url(url)

            async with aiofiles.open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(256 * 1024):
                    await f.write(chunk)

    elapsedTime = time.time() - startTime
    minutes = int(elapsedTime // 60)
    seconds = int(elapsedTime % 60)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, # type: ignore
        text= f"Download finished: {filename} \nTime: {minutes}m {seconds}s"
    )

load_dotenv()
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build() # type: ignore
    
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    grabLink_handler = MessageHandler(
        filters.TEXT & (
        filters.Entity(MessageEntity.URL) |
        filters.Entity(MessageEntity.TEXT_LINK)
        ),
        grabLink
    )
    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    application.add_handler(grabLink_handler)
    
    application.run_polling()

    # user_text = update.message.text