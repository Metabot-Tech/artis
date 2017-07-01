import os


def setup_settings():
    os.environ['DYNACONF_SETTINGS'] = "settings/settings.yml"
