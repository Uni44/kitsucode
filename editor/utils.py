# editor/utils.py

ICON_FOLDER = "📁"
ICON_PYTHON = "🐍"
ICON_BAT = "⚙️"
ICON_FILE = "📄"
ICON_JSON = "📦"
ICON_HTML = "🌐"

def icon_for_file(filename):
    if filename.endswith(".py"):
        return ICON_PYTHON
    elif filename.endswith(".bat"):
        return ICON_BAT
    elif filename.endswith(".json"):
        return ICON_JSON
    elif filename.endswith(".html"):
        return ICON_HTML
    else:
        return ICON_FILE