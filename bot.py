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
    initialMessage = await context.bot.send_message(chat_id=update.effective_chat.id, text="Starting download...") # type: ignore
    startTime = time.time()
    lastUpdateTime = startTime
    downloaded = 0

    timeout = aiohttp.ClientTimeout(total=None, sock_connect=30)
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        async with session.get(url, allow_redirects=True) as resp:

            resp.raise_for_status()

            contentType = resp.headers.get("Content-Type", "")
            if "text/html" in contentType:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, # type: ignore
                    text="Make sure the link is a direct file download."
                )
                return

            totalSize = resp.content_length
            filename = get_filename_from_url(url)

            async with aiofiles.open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    await f.write(chunk)
                    downloaded += len(chunk)

                    now = time.time()
                    if now - lastUpdateTime >= 10:
                        elapsed = now - startTime
                        speed = downloaded / elapsed if elapsed > 0 else 0

                        if totalSize:
                            percent = downloaded / totalSize * 100
                            remaining = totalSize - downloaded

                            etaSeconds = remaining / speed if speed > 0 else 0
                            etaMinutes = int(etaSeconds // 60)
                            etaSecs = int(etaSeconds % 60)
                            text = (
                                f"Downloading...\n"
                                f"{percent:.1f}%\n"
                                f"{downloaded / (1024*1024):.2f} MB / "
                                f"{totalSize / (1024*1024):.2f} MB\n"
                                f"{speed / (1024*1024):.2f} MB/s\n"
                                f"ETA: {etaMinutes}m {etaSecs}s"
                            )
                        else:
                            text = (
                                f"Downloading...\n"
                                f"{downloaded / (1024*1024):.2f} MB\n"
                                f"{speed / (1024*1024):.2f} MB/s"
                            )

                        try:
                            await initialMessage.edit_text(text)
                        except Exception:
                            pass  # ignore rate limit / edit conflicts

                        lastUpdateTime = now

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