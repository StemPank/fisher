import os
import platform
from pathlib import Path

MAIN_REPOSITORY = os.path.dirname(__file__)
RUN_AGENT_PATH = os.path.join(MAIN_REPOSITORY, "core/agent/install")


HOME_REPOSITORY = f"{os.path.join(os.environ["USERPROFILE"], "Documents") if platform.system() == "Windows" else os.path.join(Path.home(), "Documents")}/fisher"
if not os.path.exists(HOME_REPOSITORY):
    os.mkdir(HOME_REPOSITORY)
    if not os.path.exists(f"{HOME_REPOSITORY}/state"):
        os.mkdir(f"{HOME_REPOSITORY}/state")

AGENT_REPOSITORY = os.path.join(HOME_REPOSITORY, "agents")

SETTING_FILE = os.path.join(os.path.join(HOME_REPOSITORY, "state"), "setting.pkl")
STATE_FILE = os.path.join(os.path.join(HOME_REPOSITORY, "state"), "output_state.pkl")
OPERATIVE_STATE_FILE = os.path.join(os.path.join(HOME_REPOSITORY, "state"), "operative_state.pkl")

SETTING_BOT_FILE = os.path.join(os.path.join(HOME_REPOSITORY, "state"), "setting_bot.pkl")



CHAPTER = os.path.dirname(__file__)

INSTALL_BIND = os.path.join(CHAPTER, "core/agent/install")
ICONS_PATH = os.path.join(CHAPTER, "gui/icons")

CONFIG_PATH = os.path.join(CHAPTER, "gui/state")

# loggers
LOG_FILE = os.path.join(os.path.join(CHAPTER, "utils"), "app.log")

WARN_PATH = os.path.join(CHAPTER, "core/warn")