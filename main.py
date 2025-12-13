from telegram.ext import ApplicationBuilder, CommandHandler

import os

from message import create_emoticon
from util import setup_logger


def main():
    setup_logger()

    telegram_application = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_TOKEN", "NO_TOKEN"))
        .http_version("2")
        .read_timeout(600)
        .get_updates_read_timeout(600)
        .write_timeout(600)
        .get_updates_write_timeout(600)
        .pool_timeout(600)
        .get_updates_pool_timeout(600)
        .connect_timeout(600)
        .get_updates_connect_timeout(600)
        .build()
    )

    telegram_application.add_handler(
        CommandHandler("create", create_emoticon)
    )

    telegram_application.run_polling()


if __name__ == "__main__":
    main()
