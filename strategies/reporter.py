import logging
from slacker import Slacker
from dynaconf import settings

logger = logging.getLogger(__name__)


class Reporter(object):
    def __init__(self, logger):
        self.slack = Slacker(settings.SLACK.TOKEN)
        self.logger = logger

    def info(self, message):
        self.logger.info(message)
        self._post(message, {"color": "good", "message": "INFO"})

    def warning(self, message):
        self.logger.warning(message)
        self._post(message, {"color": "warning", "message": "WARNING"})

    def error(self, message):
        self.logger.error(message)
        self._post("<!here> {}".format(message), {"color": "danger", "text": "ERROR"})

    def _post(self, message, attachment):
        try:
            self.slack.chat.post_message(channel=settings.SLACK.CHANNEL,
                                         text=message,
                                         username="Artis",
                                         attachments=[attachment])
        except:
            logger.error("Failed to post to slack")
