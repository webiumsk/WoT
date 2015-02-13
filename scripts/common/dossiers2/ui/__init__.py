# Embedded file name: scripts/common/dossiers2/ui/__init__.py
from dossiers2.ui.layouts import init as ui_layouts_init
from dossiers2.ui.achievements import init as achieves_init

def init():
    achieves_init('scripts/item_defs/achievements.xml')
    ui_layouts_init()
