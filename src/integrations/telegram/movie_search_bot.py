import os
import math
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from src.services.movie_database import search_movies

load_dotenv()

# --- CONFIGURATION ---
CHANNEL_ID = int(os.getenv("MOVIE_CHANNEL_ID", "-1002478481734"))
AUTH_CHANNEL = os.getenv("AUTH_CHANNEL", "@playslands")
DELETE_TIME = int(os.getenv("SEARCH_RESULT_DELETE_SECONDS", "300"))

# --- UTILS ---
async def is_subscribed(bot, user_id):
    """Checks if the user is a member of the required channel."""
    try:
        member = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def auto_delete(context: ContextTypes.DEFAULT_TYPE):
    """Deletes a message after the specified delay."""
    job = context.job
    await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)

# --- UI LOGIC ---
def get_pagination_keyboard(results, page, query, is_index=False):
    total_results = len(results)
    total_pages = math.ceil(total_results / 10)
    start, end = page * 10, (page * 10) + 10
    page_results = results[start:end]
    
    prefix = "📂 Browse" if is_index else "🔍 Search"
    text = f"<b>{prefix}:</b> <code>{query}</code>\n📊 <b>Total:</b> {total_results} | <b>Page:</b> {page + 1}/{total_pages}\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    text += "<i>This message will self-destruct in 5 minutes.</i>\n\n"
    
    keyboard = []
    for m in page_results:
        display_name = m.get('full_title') or m['title']
        keyboard.append([InlineKeyboardButton(f"🎬 {display_name}", callback_data=f"get_{m['message_id']}")])
    
    nav = []
    cb_type = "search" if not is_index else "idxpg"
    if page > 0: nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{cb_type}_{query}_{page-1}"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"{cb_type}_{query}_{page+1}"))
    if nav: keyboard.append(nav)
    
    return text, InlineKeyboardMarkup(keyboard)

# --- HANDLERS ---
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.effective_message.reply_text(
        f"🎬 <b>Welcome {u.effective_user.first_name}!</b>\n\nI can find any movie from our database. Just type the name below.",
        parse_mode="HTML"
    )

async def handle_search(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user_id = u.effective_user.id
    
    # 1. Force Subscribe Check
    if not await is_subscribed(c.bot, user_id):
        buttons = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{AUTH_CHANNEL.replace('@','')}")]]
        await u.effective_message.reply_text(
            "❌ <b>Access Denied!</b>\n\nYou must join our update channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )
        return

    query = u.effective_message.text.strip()
    results = search_movies(query)
    
    if not results:
        await u.effective_message.reply_text("❌ No results found. Try a different spelling.")
        return

    text, markup = get_pagination_keyboard(results, 0, query)
    sent_msg = await u.effective_message.reply_text(text, reply_markup=markup, parse_mode="HTML")
    
    # 2. Schedule Auto-Delete
    c.job_queue.run_once(auto_delete, DELETE_TIME, data=sent_msg.message_id, chat_id=u.effective_chat.id)

async def cb_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query_cb = u.callback_query
    data = query_cb.data.split('_')
    
    if data[0] == "get":
        await c.bot.copy_message(chat_id=u.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=int(data[1]))
        await query_cb.answer("File sent to your PM!")
        return

    await query_cb.answer()
    # (Index and Pagination logic remains the same as previous version...)

if __name__ == '__main__':
    # Note: ApplicationBuilder now requires 'job_queue' for the auto-delete feature
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN must be set in environment")

    app = ApplicationBuilder().token(bot_token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    app.add_handler(CallbackQueryHandler(cb_handler))
    
    print("🚀 Advanced Bot Online (ForceSub + AutoDelete enabled)")
    app.run_polling()