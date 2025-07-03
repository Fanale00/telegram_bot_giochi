import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Prendi il token da variabile ambiente
TOKEN = os.getenv("BOT_TOKEN")
G2A_TAG = "gtag=347ad30297"

# Carica catalogo da file JSON
with open("catalogo_giochi.json", encoding="utf-8") as f:
    catalogo = json.load(f)

# Tastiera iniziale
def keyboard_start():
    keyboard = [
        [InlineKeyboardButton("📚 Mostra tutto il catalogo", callback_data="SHOW_ALL")],
        [InlineKeyboardButton("🔤 Scegli per lettera (A-Z)", callback_data="CHOOSE_LETTER")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Tastiera lettere A-Z
def keyboard_letters():
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

# Tastiera giochi per lettera
def keyboard_games(lettera):
    giochi = catalogo.get(lettera, {})
    keyboard = []
    for gioco in giochi.keys():
        keyboard.append([InlineKeyboardButton(gioco, callback_data=f"GAME_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna indietro", callback_data="BACK_LETTERS")])
    return InlineKeyboardMarkup(keyboard)

# Tastiera piattaforme per gioco
def keyboard_platforms(gioco):
    piattaforme = []
    for lettera, giochi in catalogo.items():
        if gioco in giochi:
            piattaforme = giochi[gioco]
            break
    keyboard = []
    for p in piattaforme:
        keyboard.append([InlineKeyboardButton(p.upper(), callback_data=f"PLAT_{p}_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna indietro", callback_data="BACK_FROM_PLATFORM")])
    return InlineKeyboardMarkup(keyboard)

# Tastiera con tutti i giochi cliccabili
def keyboard_all_games():
    keyboard = []
    for lettera in sorted(catalogo):
        giochi = catalogo[lettera]
        for gioco in giochi:
            keyboard.append([InlineKeyboardButton(f"{gioco}", callback_data=f"GAME_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna al menu iniziale", callback_data="BACK_TO_MENU")])
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Benvenuto! Cosa vuoi fare?", reply_markup=keyboard_start())

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start per iniziare a cercare giochi su G2A.")

# Gestione pulsanti
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "CHOOSE_LETTER":
        await query.edit_message_text("Scegli una lettera:", reply_markup=keyboard_letters())

    elif data == "SHOW_ALL":
        await query.edit_message_text("📚 Ecco tutti i giochi disponibili:", reply_markup=keyboard_all_games())

    elif data.startswith("LETTER_"):
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
        await query.edit_message_text(
            f"Ecco il link per **{gioco}** su **{piattaforma.upper()}**:\n{link}",
            parse_mode="Markdown"
        )

    elif data == "BACK_LETTERS":
        await query.edit_message_text("Scegli una lettera:", reply_markup=keyboard_letters())

    elif data == "BACK_TO_MENU":
        await query.edit_message_text("Benvenuto! Cosa vuoi fare?", reply_markup=keyboard_start())

    elif data == "BACK_FROM_PLATFORM":
        await query.edit_message_text("🔙 Torna al catalogo:", reply_markup=keyboard_all_games())

# Avvio del bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url="https://telegram-bot-giochi.onrender.com/"  # Cambia con il tuo dominio
    )

if __name__ == "__main__":
    main()
