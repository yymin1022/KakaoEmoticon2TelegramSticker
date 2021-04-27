apiKeyFile = open("/home/yong/server/KakaoEmoticon2TelegramSticker_KEY", 'r')
TOKEN = apiKeyFile.read().rstrip('\n')
apiKeyFile.close()

print(TOKEN)