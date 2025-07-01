import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Prendi il token da variabile d'ambiente, o metti direttamente qui (non consigliato)
TOKEN = os.getenv("BOT_TOKEN") or "IL_TUO_TOKEN_TELEGRAM"

# Il tag referral G2A da aggiungere alla fine dei link
G2A_TAG = "?gtag=347ad30297"

# Mappa piattaforme ai codici G2A usati per ricerca (usiamo query testuale, quindi non filtri)
PLATFORMS = {
    "steam": "steam",
    "ps4": "ps4",
    "ps5": "ps5",
    "xbox": "xbox",
    "pc": "pc"
}

# Carica catalogo giochi dal file JSON
with open("catalogo_giochi.json", encoding="utf-8") as f:
    catalogo = json.load(f)

# Crea la tastiera con le lettere (4 righe x 8 colonne)
def keyboard_letters():
    lettere = [chr(i) for i in range(ord('A'), ord('Z')+1)]
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

# Crea tastiera con i giochi per una lettera scelta
def keyboard_games(lettera):
    giochi = catalogo.get(lettera, {})
    keyboard = []
    for gioco in giochi.keys():
        keyboard.append([InlineKeyboardButton(gioco, callback_data=f"GAME_{gioco}")])
    keyboard.append([InlineKeyboardButton("🔙 Torna indietro", callback_data="BACK_LETTERS")])
    return InlineKeyboardMarkup(keyboard)

# Crea tastiera per piattaforme di un gioco
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Scegli una lettera:", reply_markup=keyboard_letters())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        # Costruiamo il link ricerca generico G2A + tag
        # Come da tua idea: ricerca "gioco + piattaforma" come query
        query_search = f"{gioco} {piattaforma}".replace(" ", "%20")
        link = f"https://www.g2a.com/it/category/gaming-c1?query={query_search}{G2A_TAG}"

        await query.edit_message_text(f"Ecco il link per **{gioco}** su **{piattaforma.upper()}**:\n{link}", parse_mode="Markdown")

    elif data == "BACK_LETTERS":
        await query.edit_message_text("Scegli una lettera:", reply_markup=keyboard_letters())

    elif data.startswith("BACK_GAMES_"):
        lettera = data[-1]
        await query.edit_message_text(f"Hai scelto la lettera {lettera}. Scegli un gioco:", reply_markup=keyboard_games(lettera))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start per iniziare.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
