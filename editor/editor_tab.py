from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QFont, QPainter
from PySide6.QtCore import Signal, QTimer, Qt, QSize, QRect
import os
from .code_editor import CodeEditor  # Usa la clase que ya incluye LineNumberArea
from .syntax_highlighter import PythonHighlighter
from PySide6.QtGui import QColor, QPalette

class EditorTab(QWidget):
    modified_signal = Signal(bool)

    def __init__(self, file_path, font_size=12):
        super().__init__()
        self.file_path = file_path
        self._modified = False
        self._blink = False
        self._blink_timer = QTimer()
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self.toggle_blink)

        # Crear editor con numeración y resaltador
        self.editor = CodeEditor()
        self.editor.editor_tab = self
        self.set_font_size(font_size)
        self.editor.textChanged.connect(self.on_text_changed)
        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        self.setLayout(layout)

        # Cargar archivo si existe
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self._modified = False

        self._blink_timer.stop()

    def toggle_blink(self):
        self._blink = not self._blink
        self.modified_signal.emit(self._blink)

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self._modified = False
        self._blink_timer.stop()
        self.modified_signal.emit(False)

    def is_modified(self):
        return self._modified

    def on_text_changed(self):
        if not self._modified:
            self._modified = True
            self._blink_timer.start()

    def set_font_size(self, size):
        font = QFont("Consolas", size)
        self.editor.setFont(font)
        self.editor.update_line_number_area_width()
        self.editor.update()
