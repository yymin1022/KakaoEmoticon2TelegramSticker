from telegram.ext import ApplicationBuilder, CommandHandler

from config import TELEGRAM_TOKEN
from message import create_emoticon
from util import setup_logger


def main():
    if not TELEGRAM_TOKEN:
        print("Error: Token missing")
        return

    setup_logger()

    telegram_application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    telegram_application.add_handler(
        CommandHandler("create", create_emoticon)
    )

    telegram_application.run_polling()


if __name__ == "__main__":
    main()
