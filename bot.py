import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

startMessage = "Hello. Message /link to send your direct download links for me to download. Example: /link example.com/example.zip"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=startMessage) # type: ignore

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't understand that command.") # type: ignore

load_dotenv()
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build() # type: ignore
    
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()