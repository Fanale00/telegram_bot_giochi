import json
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8144053884:AAFT3lNDRB4_tmyv1ADw38hYxsMHwib_e9U"
CATALOGO_FILE = "catalogo_giochi.json"

# Carica catalogo
with open(CATALOGO_FILE, "r", encoding="utf-8") as f:
    catalogo = json.load(f)

# Funzione per tastiera lettere (4 righe x 8 colonne)
def crea_tastiera_lettere():
    lettere = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    keyboard = []
    riga = []
    for i, lettera in enumerate(lettere, start=1):
        riga.append(InlineKeyboardButton(lettera, callback_data=f"lettera_{lettera}"))
        if i % 8 == 0:
            keyboard.append(riga)
            riga = []
    if riga:
        keyboard.append(riga)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto! Scegli una lettera per vedere i giochi disponibili:",
        reply_markup=crea_tastiera_lettere()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("lettera_"):
        lettera = data.split("_")[1]
        giochi_filtrati = [
            gioco for gioco in catalogo if gioco['nome'].upper().startswith(lettera)
        ]
        if not giochi_filtrati:
            await query.edit_message_text(f"Nessun gioco trovato con la lettera {lettera}.")
            return
        # Crea tastiera giochi (max 10 per comodità)
        keyboard = []
        for gioco in giochi_filtrati[:10]:
            keyboard.append([InlineKeyboardButton(gioco['nome'], callback_data=f"gioco_{gioco['nome']}")])
        keyboard.append([InlineKeyboardButton("⬅️ Torna alle lettere", callback_data="torna_lettere")])
        await query.edit_message_text(
            f"Giochi con la lettera {lettera}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("gioco_"):
        nome_gioco = data[6:]
        gioco = next((g for g in catalogo if g['nome'] == nome_gioco), None)
        if not gioco:
            await query.edit_message_text("Errore: gioco non trovato.")
            return
        piattaforme = gioco['piattaforme']
        keyboard = []
        for piattaforma in piattaforme:
            keyboard.append([
                InlineKeyboardButton(
                    piattaforma,
                    callback_data=f"piattaforma_{nome_gioco}_{piattaforma}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Torna ai giochi", callback_data=f"lettera_{nome_gioco[0].upper()}")])
        await query.edit_message_text(
            f"Hai scelto: {nome_gioco}\nSeleziona la piattaforma:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("piattaforma_"):
        _, nome_gioco, piattaforma = data.split("_", 2)
        gioco = next((g for g in catalogo if g['nome'] == nome_gioco), None)
        if not gioco or piattaforma not in gioco['piattaforme']:
            await query.edit_message_text("Errore: gioco o piattaforma non trovati.")
            return
        link = gioco['piattaforme'][piattaforma]['link']
        await query.edit_message_text(
            f"Ecco il link per {nome_gioco} su {piattaforma}:\n{link}"
        )

    elif data == "torna_lettere":
        await query.edit_message_text(
            "Scegli una lettera per vedere i giochi disponibili:",
            reply_markup=crea_tastiera_lettere()
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot avviato...")
    app.run_polling()

if __name__ == "__main__":
    main()
