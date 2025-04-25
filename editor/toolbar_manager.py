# editor/toolbar_manager.py
from PySide6.QtWidgets import QToolBar, QPushButton

def create_toolbar(editor):
    toolbar = QToolBar("Toolbar")

    save_btn = QPushButton("💾 Guardar")
    save_btn.clicked.connect(editor.save_current_file)
    toolbar.addWidget(save_btn)

    save_all_btn = QPushButton("💾 Guardar todo")
    save_all_btn.clicked.connect(editor.save_all_files)
    toolbar.addWidget(save_all_btn)

    buscar_btn = QPushButton("🔍 Buscar")
    toolbar.addWidget(buscar_btn)

    format_btn = QPushButton("🔧 Formatear")
    toolbar.addWidget(format_btn)

    inc_font = QPushButton("🔎+")
    inc_font.clicked.connect(lambda: editor.adjust_font_size(1))
    toolbar.addWidget(inc_font)

    dec_font = QPushButton("🔎−")
    dec_font.clicked.connect(lambda: editor.adjust_font_size(-1))
    toolbar.addWidget(dec_font)

    return toolbar