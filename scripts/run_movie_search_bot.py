from src.integrations.telegram.movie_search_bot import start, handle_search, cb_handler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN must be set in environment")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.run_polling()
