import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
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
                Image.open(await img.read()).resize((512, 512)).save(img_bytes, "png")
                stickers.append(InputSticker(img_bytes.getvalue(), ["😀"]))
    curTime = str(datetime.datetime.utcnow().timestamp()).replace(".", "")
    stickerName = f"t{curTime}_by_{context.bot.name}" % (curTime)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"총 {len(emoticonMeta['thumbnailUrls'])}개의 이모티콘을 텔레그램 서버로 업로드합니다.",
    )

    await context.bot.create_new_sticker_set(
        user_id=context.bot.id,
        name=stickerName,
        title=emoticonMeta["title"],
        sticker_format=StickerFormat.STATIC,
        stickers=stickers,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"{emoticonMeta['title']} 스티커 생성이 완료되었습니다!"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="https://t.me/addstickers/%s" % (stickerName),
    )


async def helpMenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Help Menu")


async def startBot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Bot Started!"
    )


if __name__ == "__main__":
    application = (
        ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN", "NO_TOKEN")).build()
    )

    application.add_handlers(
        [
            CommandHandler("start", startBot),
            CommandHandler("help", helpMenu),
            CommandHandler("create", createEmoticon),
        ]
    )

    application.run_polling()