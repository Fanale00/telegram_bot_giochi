import os
import json
from flask import Flask, request, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
G2A_TAG = "gtag=347ad30297"

with open("catalogo_giochi.json", encoding="utf-8") as f:
    catalogo = json.load(f)

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Inserisci qui i tuoi handler come prima, per esempio start, button_handler ecc.

def keyboard_letters():
    # ... (tua funzione come prima)
    lettere = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    keyboard = []
    row = []
    for i, lettera in enumerate(lettere, 1):
        row.append(InlineKeyboardButton(lettera, callback_data=f"LETTER_{lettera}"))
        if i % 8 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def keyboard_games(lettera):
    giochi = catalogo.get(lettera, {})
    keyboard = []
    for gioco in giochi.keys():
        keyboard.append([InlineKeyboardButton(gioco, callback_data=f"GAME_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna indietro", callback_data="BACK_LETTERS")])
    return InlineKeyboardMarkup(keyboard)

def keyboard_platforms(gioco):
    piattaforme = []
    for lettera, giochi in catalogo.items():
        if gioco in giochi:
            piattaforme = giochi[gioco]
            break
    keyboard = []
    for p in piattaforme:
        keyboard.append([InlineKeyboardButton(p.upper(), callback_data=f"PLAT_{p}_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna indietro", callback_data=f"BACK_GAMES_{gioco[0].upper()}")])
    return InlineKeyboardMarkup(keyboard)

from telegram.ext import CallbackContext

async def start(update, context):
    await update.message.reply_text("Ciao! Scegli una lettera:", reply_markup=keyboard_letters())

async def help_command(update, context):
    await update.message.reply_text("Usa /start per iniziare.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("LETTER_"):
        lettera = data.split("_")[1]
        await query.edit_message_text(f"Hai scelto la lettera {lettera}. Scegli un gioco:", reply_markup=keyboard_games(lettera))

    elif data.startswith("GAME_"):
        gioco = data[len("GAME_"):]
        await query.edit_message_text(f"Hai scelto il gioco: {gioco}. Seleziona la piattaforma:", reply_markup=keyboard_platforms(gioco))

    elif data.startswith("PLAT_"):
        parts = data.split("_", 2)
        piattaforma = parts[1]
        gioco = parts[2]
        query_search = f"{gioco} {piattaforma}".replace(" ", "%20")
        link = f"https://www.g2a.com/it/category/gaming-c1?query={query_search}&{G2A_TAG}"
        await query.edit_message_text(f"Ecco il link per **{gioco}** su **{piattaforma.upper()}**:\n{link}", parse_mode="Markdown")

    elif data == "BACK_LETTERS":
        await query.edit_message_text("Scegli una lettera:", reply_markup=keyboard_letters())

    elif data.startswith("BACK_GAMES_"):
        lettera = data[-1]
        await query.edit_message_text(f"Hai scelto la lettera {lettera}. Scegli un gioco:", reply_markup=keyboard_games(lettera))

from telegram import Update
from telegram.ext import ApplicationBuilder

# Registra gli handler nel dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# Endpoint per Telegram webhook
@app.route('/', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return Response('ok', status=200)

# Endpoint health check
@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8443))
    app.run(host='0.0.0.0', port=port)
