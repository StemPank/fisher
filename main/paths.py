import os

CHAPTER = os.path.dirname(__file__)

INSTALL_BIND = os.path.join(CHAPTER, "core/agent/install")
ICONS_PATH = os.path.join(CHAPTER, "gui/icons")

RUN_AGENT_PATH = os.path.join(CHAPTER, "core/agent")
SETTING_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "setting.pkl")
CONFIG_PATH = os.path.join(CHAPTER, "gui/state")
# AGENT_FILE = os.path.join(os.path.join(CHAPTER, "../gui/agent"), "agent.pkl")
STATE_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "output_state.pkl")
OPERATIVE_STATE_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "operative_state.pkl")

# loggers
LOG_FILE = os.path.join(os.path.join(CHAPTER, "utils"), "app.log")

WARN_PATH = os.path.join(CHAPTER, "core/warn")