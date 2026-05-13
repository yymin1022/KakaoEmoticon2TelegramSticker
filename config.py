import logging
import os
import re


EMOTICON_ID_REGEX = re.compile(r"^https://e\.kakao\.com/t/[a-zA-Z0-9_-]+$")
LOG_LEVEL = logging.INFO
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")