import os

CHAPTER = os.path.dirname(__file__)
RUN_AGENT_PATH = os.path.join(CHAPTER, "core")
SETTING_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "setting.pkl")
CONFIG_PATH = os.path.join(CHAPTER, "gui/state")
# AGENT_FILE = os.path.join(os.path.join(CHAPTER, "../gui/agent"), "agent.pkl")
STATE_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "output_state.pkl")
OPERATIVE_STATE_FILE = os.path.join(os.path.join(CHAPTER, "gui/state"), "operative_state.pkl")
ICONS_PATH = os.path.join(CHAPTER, "gui/icons")