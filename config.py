import logging
import os
import re


EMOTICON_ID_REGEX = re.compile("https://e.kakao.com/t/.+")
LOG_LEVEL = logging.INFO
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")