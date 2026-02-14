import os
import math
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from database import search_movies, get_all_movies

load_dotenv()

def get_pagination_keyboard(results, page, query):
    total_results = len(results)
    total_pages = math.ceil(total_results / 10)
    start, end = page * 10, (page * 10) + 10
    page_results = results[start:end]
    
    # UI Header - showing if results are exact or related
    text = f"🔍 <b>Search for:</b> <code>{query}</code>\n"
    text += f"📊 <b>Results Found:</b> {total_results} | <b>Page:</b> {page + 1}/{total_pages}\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    for m in page_results:
        clean_display_title = m['title'].replace("**", "").replace("__", "").strip()
        text += f"🎬 <b>{clean_display_title}</b>\n"
        text += f"🔗 <a href='{m['link']}'>Click here to View Post</a>\n\n"
    
    buttons = []
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"search_{query}_{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"search_{query}_{page+1}"))
    
    if nav_row: buttons.append(nav_row)
    return text, InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("🎬 <b>Welcome!</b>\nJust type a movie name to search.", parse_mode="HTML")

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text: return
    
    query = message.text.strip()
    if query.startswith('/'): return
    
    results = search_movies(query)
    
    if not results:
        # If no exact or related match found
        await message.reply_text("No result found please check your spelling ..")
        return
    
    text, markup = get_pagination_keyboard(results, 0, query)
    await message.reply_text(text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

async def pg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_cb = update.callback_query
    await query_cb.answer()
    
    # Callback data parsing
    data_parts = query_cb.data.split('_')
    user_query = data_parts[1]
    page = int(data_parts[2])
    
    results = search_movies(user_query)
    text, markup = get_pagination_keyboard(results, page, user_query)
    
    await query_cb.edit_message_text(text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pg_callback, pattern="^search_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    print("🚀 Smart Search Bot is live...")
    app.run_polling()