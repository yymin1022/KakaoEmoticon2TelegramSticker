import telegram
from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater

apiKeyFile = open("/home/server/KakaoEmoticon2TelegramSticker_KEY", 'r')
TOKEN = apiKeyFile.read().rstrip('\n')
apiKeyFile.close()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def createEmoticon(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Create Command")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, World!")

create_handler = CommandHandler("create", createEmoticon)
start_handler = CommandHandler("start", start)

dispatcher.add_handler(create_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()