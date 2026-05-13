import datetime

from io import BytesIO
from json import JSONDecodeError
from typing import TypedDict, List

from PIL import Image
from aiohttp import ClientError, ClientSession
from telegram import Update, InputSticker
from telegram.constants import StickerFormat
from telegram.ext import ContextTypes

from config import EMOTICON_ID_REGEX


class EmoticonMeta(TypedDict):
    title: str
    thumbnailUrls: List[str]

async def create_emoticon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.effective_user:
        return

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="URL을 입력해주세요.",
        )
        return

    emoticon_url = context.args[0]

    if not EMOTICON_ID_REGEX.match(emoticon_url):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="유효한 이모티콘 URL이 아닙니다.",
        )

        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="이모티콘 정보를 불러오는 중입니다.",
    )

    emoticon_url = emoticon_url.replace(
        "https://e.kakao.com/t/",
        "https://e.kakao.com/api/items/",
    )

    async with ClientSession() as session:
        try:
            async with session.get(emoticon_url) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except (ClientError, JSONDecodeError):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="이모티콘 정보를 가져올 수 없습니다.",
            )
            return

        items = data["contents"]["items"]
        if not items:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="이모티콘 목록이 비어 있습니다.",
            )
            return

        emoticon_meta = EmoticonMeta(
            title=data["hero"]["title"],
            thumbnailUrls=[item["thumbnailUrl"] for item in items],
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{emoticon_meta['title']} 이모티콘을 다운로드 합니다.",
        )

        stickers: List[InputSticker] = []

        for emoticon in emoticon_meta["thumbnailUrls"]:
            async with session.get(emoticon) as img:
                img_bytes = BytesIO()
                Image.open(BytesIO(await img.read())).resize((512, 512)).save(
                    img_bytes, "png"
                )
                stickers.append(
                    InputSticker(
                        sticker=img_bytes.getvalue(),
                        emoji_list=["😀"],
                        format=StickerFormat.STATIC
                    )
                )
    cur_time = str(datetime.datetime.now(datetime.timezone.utc).timestamp()).replace(".", "")
    sticker_name = f"t{cur_time}_by_{context.bot.name[1:]}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"총 {len(emoticon_meta['thumbnailUrls'])}개의 이모티콘을 텔레그램 서버로 업로드합니다.",
    )

    doing_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"업로드 중... (0/{len(emoticon_meta['thumbnailUrls'])})",
    )

    await context.bot.create_new_sticker_set(
        user_id=update.effective_user.id,
        name=sticker_name,
        title=emoticon_meta["title"],
        stickers=[stickers[0]],
    )

    await doing_message.edit_text(
        text=f"업로드 중... (1/{len(emoticon_meta['thumbnailUrls'])})",
    )

    for index, sticker in enumerate(stickers[1:], 2):
        await context.bot.add_sticker_to_set(
            user_id=update.effective_user.id,
            name=sticker_name,
            sticker=sticker,
        )
        await doing_message.edit_text(
            text=f"업로드 중... ({index}/{len(emoticon_meta['thumbnailUrls'])})",
        )

    await doing_message.edit_text(
        text=f"{emoticon_meta['title']} 스티커 생성이 완료되었습니다!",
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"https://t.me/addstickers/{sticker_name}",
    )