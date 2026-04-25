import logging
import os
from dotenv import load_dotenv
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

startMessage = "Hello. Send me a link for me to download. Example: example.com/example.zip"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=startMessage) # type: ignore

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't understand that command.") # type: ignore

async def grabLink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text # type: ignore
    await context.bot.send_message(chat_id=update.effective_chat.id, text=user_text) # type: ignore

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