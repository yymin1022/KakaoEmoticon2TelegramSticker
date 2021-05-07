from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater
import telegram

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
import requests
import urllib.request

apiKeyFile = open("/home/server/KakaoEmoticon2TelegramSticker_KEY", 'r')
TOKEN = apiKeyFile.read().rstrip('\n')
apiKeyFile.close()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def createEmoticon(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="카카오 이모티콘 서비스에 접속하는 중입니다.")

    emoticonURL = context.args[0]
    soupHeader = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(executable_path='/home/server/KakaoEmoticon2TelegramSticker/chromedriver', chrome_options=options)
    url = 'https://e.kakao.com/t/uh-uh-uh-ver-2'
    driver.get(url)

    context.bot.send_message(chat_id=update.effective_chat.id, text="이모티콘 정보를 불러오는 중입니다.")

    pageResource = driver.page_source
    soup = BeautifulSoup(pageResource, features="html.parser")

    divRoot = soup.find("div", id="root")
    divWrap = divRoot.find("div", id="kakaoWrap")
    divContent = divWrap.find("div", id="kakaoContent")
    divInfo = divContent.find("div", class_="area_product")
    divTitle = divInfo.find("div", class_="info_product")
    strTitle = divTitle.find("h3", class_="tit_product")
    context.bot.send_message(chat_id=update.effective_chat.id, text="%s 이모티콘을 다운로드 합니다."%(strTitle.text))

    divEmoticons = divContent.find("div", class_="area_emoticon")
    listEmoticons = divEmoticons.find("ul")
    itemEmoticons = listEmoticons.find_all("li")

    count = 0
    arrEmoticon = []

    for srcEmoticon in itemEmoticons:
        urlEmoticon = srcEmoticon.find("img")["src"]
        urllib.request.urlretrieve(urlEmoticon, "emoticonTemp/" + str(count) + ".png")

        pngEmoticon = open("emoticonTemp/" + str(count) + ".png", "rb")
        arrEmoticon.append(pngEmoticon)

        count += 1
    
    createNewStickerSet (1234, strTitle.text, "", False, arrEmoticon)
    context.bot.send_message(chat_id=update.effective_chat.id, text=str(arrEmoticon))

def helpMenu(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Help Menu")

def startBot(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot Started!")

create_handler = CommandHandler("create", createEmoticon)
help_handler = CommandHandler("help", helpMenu)
start_handler = CommandHandler("start", startBot)

dispatcher.add_handler(create_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()