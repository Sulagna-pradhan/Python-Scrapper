import os
import math
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from database import search_movies, get_movies_by_letter

load_dotenv()

def get_pagination_keyboard(results, page, query, is_index=False):
    total_results = len(results)
    total_pages = math.ceil(total_results / 10)
    start, end = page * 10, (page * 10) + 10
    page_results = results[start:end]
    
    prefix = "📂 Browse" if is_index else "🔍 Search"
    text = f"<b>{prefix}:</b> <code>{query}</code>\n📊 <b>Total:</b> {total_results} | <b>Page:</b> {page + 1}/{total_pages}\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
    
    for m in page_results:
        # We display the FULL technical title, but keep the link clean
        display_name = m.get('full_title') or m['title']
        text += f"🎬 <b>{display_name}</b>\n"
        text += f"🔗 <a href='{m['link']}'>Click here to View Post</a>\n\n"
    
    nav = []
    cb_type = "search" if not is_index else "idxpg"
    if page > 0: nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{cb_type}_{query}_{page-1}"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"{cb_type}_{query}_{page+1}"))
    
    return text, InlineKeyboardMarkup([nav]) if nav else None

def get_alphabet_keyboard():
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyboard = [ [InlineKeyboardButton(char, callback_data=f"idx_{char}") for char in alphabet[i:i+5]] for i in range(0, len(alphabet), 5) ]
    return InlineKeyboardMarkup(keyboard)

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.effective_message.reply_text("🎬 <b>Welcome!</b>\nType a movie name to search or /index to browse.", parse_mode="HTML")

async def index_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.effective_message.reply_text("📂 <b>Select a letter:</b>", reply_markup=get_alphabet_keyboard(), parse_mode="HTML")

async def handle_search(u: Update, c: ContextTypes.DEFAULT_TYPE):
    msg = u.effective_message
    if not msg or not msg.text or msg.text.startswith('/'): return
    query = msg.text.strip()
    results = search_movies(query)
    if not results:
        await msg.reply_text("No result found please check your spelling ..")
        return
    text, markup = get_pagination_keyboard(results, 0, query)
    await msg.reply_text(text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

async def cb_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query_cb = u.callback_query
    await query_cb.answer()
    data = query_cb.data.split('_')
    
    if data[0] == "idx":
        res = get_movies_by_letter(data[1])
        text, markup = get_pagination_keyboard(res, 0, data[1], is_index=True) if res else (f"❌ No movies for {data[1]}", None)
        await query_cb.edit_message_text(text, reply_markup=markup or get_alphabet_keyboard(), parse_mode="HTML", disable_web_page_preview=True)
    elif data[0] in ["search", "idxpg"]:
        is_idx = data[0] == "idxpg"
        res = get_movies_by_letter(data[1]) if is_idx else search_movies(data[1])
        text, markup = get_pagination_keyboard(res, int(data[2]), data[1], is_index=is_idx)
        await query_cb.edit_message_text(text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("index", index_cmd))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    print("🚀 All systems online with Dual-Title support!")
    app.run_polling()