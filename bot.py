import logging
import os
from dotenv import load_dotenv
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import aiohttp
from urllib.parse import urlparse

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


async def download_file(url: str, output_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:

            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "")

            if "text/html" in content_type:
                text = await resp.text()
                raise ValueError(
                    "URL returned HTML instead of a file."
                    "Likely a redirect/login page or invalid direct download link."
                )

            with open(output_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)

            return resp.headers

async def grabLink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url: str = update.message.text # type: ignore
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Download started...") # type: ignore

    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:

            resp.raise_for_status()

            filename = get_filename_from_url(url)

            if "text/html" in resp.headers.get("Content-Type", ""):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, # type: ignore
                    text="Make sure the link is a download link."
                )
                return

            with open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, # type: ignore
        text=f"Download finished: {filename}"
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