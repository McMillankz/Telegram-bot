import berserk
import chess.pgn
from stockfish import Stockfish
import logging
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler, ApplicationBuilder

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я могу показать рейтинг игроков на lichess.org. Для этого введи команду /stats <никнейм_игрока>.')

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ой, извините, команда недоступна в вашем регионе")

async def stockfish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.args[0]
    session = berserk.TokenSession("lip_KF49HPZT8GEgnRlk2LJG")
    client = berserk.Client(session=session)
    stockfish = Stockfish(path='C:/Users/mcmil/OneDrive/Documents/Telegram bot/stockfish/stockfish.exe', depth=23)

    user = user.replace("https://lichess.org/", "")
    if "/black" in user:
        user = user.replace("/black", "")
        player_color = "Black"
    else:
        player_color = "White"

    pgn = client.games.export(user, as_pgn=True)
    with open(f'{user}.pgn', 'w') as f:
        f.write(pgn)
    pgn = open(f"{user}.pgn")

    mygame=chess.pgn.read_game(pgn)
    old_result = 0
    n = 1
    player_color = "Black"
    while mygame.next():
        mygame = mygame.next()
        n = n+1
        if player_color == "White" and n % 2 != 0:
            continue

        if player_color == "Black" and n % 2 == 0:
            continue
        
        position = mygame.board().fen()
        stockfish.set_fen_position(position)
        result = stockfish.get_evaluation()
        if int(result['value']) - int(old_result) > 200:
            message = f"Долбаеб, ты с {n//2} хода потерял преимущество..."
            break
        old_result = int(result['value'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6620100386:AAEwqIT6s7W2vgArMlYj7l-Rok73qrU2Buw").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler('user', stockfish))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()