import logging


class ColorFormatter(logging.Formatter):
    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
from telegram import Update, InputSticker
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler
from telegram.constants import StickerFormat

from PIL import Image

from aiohttp import ClientSession

import datetime
import os
from io import BytesIO
from re import compile
from typing import TypedDict, List, Sequence


class EmoticonMeta(TypedDict):
    title: str
    thumbnailUrls: List[str]


EMOTICON_ID_REGEX = compile("https://e.kakao.com/t/.+")


async def createEmoticon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat
    assert context.args

    emoticonURL = context.args[0]

    if not EMOTICON_ID_REGEX.match(emoticonURL):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="유효한 이모티콘 URL이 아닙니다."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="이모티콘 정보를 불러오는 중입니다."
    )

    emoticonURL = emoticonURL.replace(
        "https://e.kakao.com/t/", "https://e.kakao.com/api/v1/items/t/"
    )

    async with ClientSession() as session:
        async with session.get(emoticonURL) as resp:
            emoticonMeta = EmoticonMeta((await resp.json())["result"])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{emoticonMeta['title']} 이모티콘을 다운로드 합니다.",
        )

        stickers: Sequence[InputSticker] = []

        for emoticon in emoticonMeta["thumbnailUrls"]:
            async with session.get(emoticon) as img:
                img_bytes = BytesIO()
                Image.open(BytesIO(await img.read())).resize((512, 512)).save(
                    img_bytes, "png"
                )
                stickers.append(InputSticker(img_bytes.getvalue(), ["😀"]))
    curTime = str(datetime.datetime.now(datetime.UTC).timestamp()).replace(".", "")
    stickerName = f"t{curTime}_by_{context.bot.name[1:]}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"총 {len(emoticonMeta['thumbnailUrls'])}개의 이모티콘을 텔레그램 서버로 업로드합니다.",
    )
    assert update.effective_user

    doing_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"업로드 중... (0/{len(emoticonMeta['thumbnailUrls'])})",
    )

    await context.bot.create_new_sticker_set(
        user_id=update.effective_user.id,
        name=stickerName,
        title=emoticonMeta["title"],
        sticker_format=StickerFormat.STATIC,
        stickers=[stickers[0]],
    )

    await doing_message.edit_text(
        text=f"업로드 중... (1/{len(emoticonMeta['thumbnailUrls'])})"
    )

    for index, sticker in enumerate(stickers[1:], 2):
        await context.bot.add_sticker_to_set(
            user_id=update.effective_user.id, name=stickerName, sticker=sticker
        )
        await doing_message.edit_text(
            text=f"업로드 중... ({index}/{len(emoticonMeta['thumbnailUrls'])})"
        )

    await doing_message.edit_text(text=f"{emoticonMeta['title']} 스티커 생성이 완료되었습니다!")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="https://t.me/addstickers/%s" % (stickerName),
    )


if __name__ == "__main__":
    application = (
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

    application.add_handlers(
        [
            CommandHandler("create", createEmoticon),
        ]
    )

    application.run_polling()
