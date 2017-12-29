import logging
from slacker import Slacker
from dynaconf import settings

logger = logging.getLogger(__name__)


class Reporter(object):
    def __init__(self):
        self.slack = Slacker(settings.SLACK.TOKEN)

    def info(self, message):
        self._post("[INFO] {}".format(message))

    def warning(self, message):
        self._post("[WARNING] {}".format(message))

    def error(self, message):
        self._post("[ERROR] {}".format(message))

    def _post(self, message):
        try:
            self.slack.chat.post_message(channel=settings.SLACK.CHANNEL,
                                         text=message,
                                         username="Artis")
        except:
            logger.error("Failed to post to slack")
