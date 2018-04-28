import logging
import time
from slacker import Slacker
from dynaconf import settings

logger = logging.getLogger(__name__)


class Cooldown(object):
    def __init__(self, message, duration):
        self.message = message
        self.duration = duration
        self.start = time.time()


class Reporter(object):
    def __init__(self, logger=None):
        self.slack = Slacker(settings.SLACK.TOKEN)
        self.logger = logger
        self.cooldowns = []

    def info(self, message, slack_cooldown=0):
        if self.logger is not None:
            self.logger.info(message)
        self._post(message, slack_cooldown, {"color": "good", "text": "INFO"})

    def warning(self, message, slack_cooldown=0):
        if self.logger is not None:
            self.logger.warning(message)
        self._post(message, slack_cooldown, {"color": "warning", "text": "WARNING"})

    def error(self, message, slack_cooldown=0):
        if self.logger is not None:
            self.logger.error(message)
        self._post("<!here> {}".format(message), slack_cooldown, {"color": "danger", "text": "ERROR"})

    def _can_trigger(self, message):
        for cooldown in reversed(self.cooldowns):
            if cooldown.message != message:
                continue

            if time.time() > cooldown.start + cooldown.duration:
                self.cooldowns.remove(cooldown)
                return True
            else:
                return False

        return True

    def _post(self, message, cooldown, attachment):
        if not self._can_trigger(message):
            return

        try:
            self.slack.chat.post_message(channel=settings.SLACK.CHANNEL,
                                         text=message,
                                         attachments=[attachment])
        except:
            logger.error("Failed to post to slack")

        if cooldown > 0:
            self.cooldowns.append(Cooldown(message, cooldown))
