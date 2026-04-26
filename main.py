import os, asyncio, aiosqlite
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION ---
# Get your ID from @userinfobot and replace 12345678
ADMIN_ID = 12345678 
TOKEN = os.environ.get("BOT_TOKEN")

# --- 2. DATABASE (Saves your users and money) ---
async def init_db():
    async with aiosqlite.connect("tmadbot.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users 
            (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 5.0, refs INTEGER DEFAULT 0)''')
        await db.commit()

# --- 3. AMHARIC BUTTONS (The UI) ---
MENU = ReplyKeyboardMarkup([
    ['💰 ሂሳብ (Balance)', '🎁 ስጦታ (Daily)'],
    ['🔗 መጋበዣ (Invite)', '💳 ወጪ ማድረግ (Withdraw)'],
    ['ℹ️ እርዳታ (Help)']
], resize_keyboard=True)

# --- 4. BOT FUNCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    async with aiosqlite.connect("tmadbot.db") as db:
        # This adds the user and gives them the 5 ETB signup bonus automatically
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        await db.commit()
    
    welcome_text = (
        "<b>እንኳን ወደ TM Ads Bot በደህና መጡ! 🎉</b>\n\n"
        "እዚህ ጓደኞቻቸውን በመጋበዝ እና ስራዎችን በመስራት የሞባይል ካርድ ወይም ብር ማግኘት ይችላሉ።\n\n"
        "🎁 <b>የመመዝገቢያ ስጦታ:</b> 5 ETB ተሰጥቶዎታል።"
    )
    await update.message.reply_text(welcome_text, reply_markup=MENU, parse_mode="HTML")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    async with aiosqlite.connect("tmadbot.db") as db:
        async with db.execute("SELECT balance, refs FROM users WHERE user_id=?", (uid,)) as c:
            row = await c.fetchone()
            if row:
                text = (
                    f"📊 <b>የአካውንት መረጃ</b>\n\n"
                    f"💰 <b>ሂሳብ:</b> {row[0]} ETB\n"
                    f"👥 <b>የጋበዟቸው ሰዎች:</b> {row[1]}\n"
                    f"📅 <b>ሁኔታ:</b> Active ✅"
                )
                await update.message.reply_text(text, parse_mode="HTML")

# --- 5. SERVER FOR RENDER (Keep-Alive) ---
app = Flask('')
@app.route('/')
def home(): return "TM Ads Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- 6. STARTING THE ENGINE ---
if __name__ == '__main__':
    # Start the "Keep Alive" web server
    Thread(target=run).start()
    
    # Setup Database and Bot
    asyncio.run(init_db())
    
    if not TOKEN:
        print("❌ Error: BOT_TOKEN not found in Environment Variables!")
    else:
        bot = ApplicationBuilder().token(TOKEN).build()
        
        # Commands
        bot.add_handler(CommandHandler("start", start))
        
        # Button Messages
        bot.add_handler(MessageHandler(filters.Text("💰 ሂሳብ (Balance)"), balance))
        
        print("🚀 TM Ads Bot is starting...")
        bot.run_polling()
