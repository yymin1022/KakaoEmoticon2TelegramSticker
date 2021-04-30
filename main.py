from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater
import telegram

from bs4 import BeautifulSoup
import requests

apiKeyFile = open("/home/server/KakaoEmoticon2TelegramSticker_KEY", 'r')
TOKEN = apiKeyFile.read().rstrip('\n')
apiKeyFile.close()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def createEmoticon(update, context):
    emoticonURL = context.args[0]
    soupHeader = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    
    pageResource = requests.get(emoticonURL, headers=soupHeader)
    soup = BeautifulSoup(pageResource.text, features="html.parser")

    divContent = soup.find("div", id="kakaoContent")
    context.bot.send_message(chat_id=update.effective_chat.id, text=divContent)
    divInfo = divContent.find("div", class_="area_product")
    context.bot.send_message(chat_id=update.effective_chat.id, text=divInfo)
    divTitle = divInfo.find("div", class_="info_product")
    context.bot.send_message(chat_id=update.effective_chat.id, text=divTitle)
    strTitle = divTitle.find_all("span", class_="tit_inner")[0]

    divEmoticons = divContent.find("div", class_="area_emoticon")
    listEmoticons = divEmoticons.find("ul")
    itemEmoticons = listEmoticons.find_all("li")

    context.bot.send_message(chat_id=update.effective_chat.id, text=strTitle)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot Started!")

create_handler = CommandHandler("create", createEmoticon)
start_handler = CommandHandler("start", start)

dispatcher.add_handler(create_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()