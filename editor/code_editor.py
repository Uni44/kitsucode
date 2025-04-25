from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtGui import QPainter, QTextFormat, QColor, QFont, QTextCursor
from PySide6.QtCore import Qt, QRect, QSize, QTimer
from .syntax_highlighter import PythonHighlighter
import json
import jedi
from PySide6.QtWidgets import QListWidget, QListWidgetItem
import time
from PySide6.QtGui import QFontMetrics

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.line_number_area_size()

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.error_lines = set()
        self.match_lines = set()
        self.last_keypress_time = 0  # Marca de tiempo de la última tecla
        self.debounce_delay = 300  # Tiempo de espera en milisegundos

        self.setFont(QFont("Consolas", 12))
        self.highlighter = PythonHighlighter(self.document())
        self.colors = self.highlighter.get_loaded_colors()
        
        # Configuración de estilo
        bg = self.colors.get("background", "#1e1e1e")
        fg = self.colors.get("editor_foreground", "#ffffff")
        self.setStyleSheet(f"background-color: {bg}; color: {fg};")

        # Área de números de línea
        self.line_number_area = LineNumberArea(self)

        # Lista de autocompletado
        self.completion_list = QListWidget(self)
        self.completion_list.hide()
        self.completion_list.itemClicked.connect(self.insert_completion)

        # Conexiones
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.selectionChanged.connect(lambda: QTimer.singleShot(0, self.highlight_matching_words))

        # Ajustes iniciales
        self.update_line_number_area_width()
        self.cursorPositionChanged.connect(lambda: self.line_number_area.update())

    def set_error_lines(self, lines):
        self.error_lines = set(lines)
        self.line_number_area.update()

    def set_match_lines(self, lines):
        self.match_lines = set(lines)
        self.line_number_area.update()

    def draw_indent_guides(self, painter):
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        font_metrics = self.fontMetrics()
        space_width = font_metrics.horizontalAdvance(' ')

        while block.isValid() and top <= self.viewport().rect().bottom():
            text = block.text()
            indent_level = 0

            for ch in text:
                if ch == ' ':
                    indent_level += 1
                elif ch == '\t':
                    indent_level += 4  # suponiendo 1 tab = 4 espacios
                else:
                    break

            for i in range(indent_level // 4):  # 1 guía por cada 4 espacios
                x = self.contentOffset().x() + (i + 1) * 4 * space_width
                painter.setPen(self.colors.get("intent_line", "#242424"))
                painter.drawLine(x, top, x, bottom)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        self.draw_indent_guides(painter)
        self.draw_scroll_markers(painter)

    def draw_scroll_markers(self, painter):
        visible_rect = self.viewport().rect()
        total_blocks = self.blockCount()
        editor_height = self.viewport().height()

        block = self.document().firstBlock()
        line_number = 1

        while block.isValid():
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            ratio = line_number / total_blocks
            y = int(editor_height * ratio)

            if line_number in self.error_lines:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#ff5555"))
                painter.drawRect(visible_rect.right() - 4, y, 4, 2)

            elif line_number in self.match_lines:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#f1fa8c"))
                painter.drawRect(visible_rect.right() - 4, y, 4, 2)

            elif line_number == self.textCursor().blockNumber() + 1:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(self.colors.get("cursor_marker", "#00ffff")))
                painter.drawRect(visible_rect.right() - 4, y, 4, 2)


            line_number += 1
            block = block.next()

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        key = event.key()
        tab_spaces = "    "  # 4 espacios
    
        current_time = time.time() * 1000  # Marca de tiempo en milisegundos
    
        # TAB: autocompletar o insertar sangría
        if key == Qt.Key_Tab:
            if self.completion_list.isVisible() and self.completion_list.count() > 0:
                selected_item = self.completion_list.item(0)
                if selected_item:
                    self.insert_completion(selected_item)
                    event.accept()
                    return
            else:
                # Si hay varias líneas seleccionadas, indentar cada línea
                if cursor.hasSelection():
                    start = cursor.selectionStart()
                    end = cursor.selectionEnd()
    
                    cursor.setPosition(start)
                    start_block = cursor.blockNumber()
    
                    cursor.setPosition(end)
                    # No indentar la última línea si está seleccionada solo su inicio
                    if cursor.positionInBlock() == 0 and end != start:
                        end_block = cursor.blockNumber() - 1
                    else:
                        end_block = cursor.blockNumber()
    
                    cursor.beginEditBlock()
                    for block_num in range(start_block, end_block + 1):
                        block = self.document().findBlockByNumber(block_num)
                        position = block.position()
    
                        cursor.setPosition(position)
                        cursor.insertText(tab_spaces)
                    cursor.endEditBlock()
                else:
                    # Solo una línea o sin selección → insertar espacios normales
                    self.insertPlainText(tab_spaces)
    
                event.accept()
                return
    
        # SHIFT + TAB: quitar sangría si hay
        elif key == Qt.Key_Backtab:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
    
            cursor.setPosition(start)
            start_block = cursor.blockNumber()
    
            cursor.setPosition(end)
            end_block = cursor.blockNumber()
    
            cursor.beginEditBlock()
            for block_num in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(block_num)
                position = block.position()
    
                cursor.setPosition(position)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)
                selected_text = cursor.selectedText()
                if selected_text == "    ":
                    cursor.removeSelectedText()
            cursor.endEditBlock()
            event.accept()
            return
    
        # Si no es tabulador, seguir con el comportamiento normal
        super().keyPressEvent(event)
    
        # Autocompletado Jedi
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
    
        if len(word) >= 2 and current_time - self.last_keypress_time > self.debounce_delay:
            self.last_keypress_time = current_time
            text = self.toPlainText()
            try:
                script = jedi.Script(code=text, path="")
                completions = script.complete()
            except Exception as e:
                self.completion_list.hide()
                return
    
            if completions:
                self.completion_list.clear()
                for c in completions:
                    item = QListWidgetItem(c.name_with_symbols)
                    self.completion_list.addItem(item)
    
                rect = self.cursorRect()
                self.completion_list.setGeometry(rect.x(), rect.y() + rect.height(), 300, 100)
                self.completion_list.show()
            else:
                self.completion_list.hide()
        else:
            self.completion_list.hide()

    def insert_completion(self, item):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(item.text())  # Insertar la sugerencia completa
        self.setTextCursor(cursor)
        self.completion_list.hide()  # Cerrar la ventana de autocompletado
    
    def focusOutEvent(self, event):
        # Cerrar la ventana de autocompletado si se hace clic fuera
        self.completion_list.hide()
        super().focusOutEvent(event)
    
    def mousePressEvent(self, event):
        # Si se hace clic en cualquier parte del editor, cerrar el autocompletado si está visible
        if not self.completion_list.rect().contains(event.pos()):
            self.completion_list.hide()
        super().mousePressEvent(event)
        
    def highlight_matching_words(self):
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        selections = []

        self.match_lines = set()  # ✅ Siempre limpiar primero

        if selected_text and len(selected_text) > 1 and selected_text.isidentifier():
            doc = self.document()
            highlight_cursor = QTextCursor(doc)

            while not highlight_cursor.isNull() and not highlight_cursor.atEnd():
                highlight_cursor = doc.find(selected_text, highlight_cursor)
                if not highlight_cursor.isNull():
                    selection = QTextEdit.ExtraSelection()
                    fmt = selection.format
                    fmt.setBackground(QColor(self.colors.get("highlight_match", "#44475a")))
                    fmt.setForeground(QColor(self.colors.get("match_foreground", "#ffffff")))
                    selection.cursor = highlight_cursor
                    selections.append(selection)

                    # 🎯 Agregamos la línea del match
                    line = highlight_cursor.blockNumber() + 1
                    self.match_lines.add(line)

        if not self.isReadOnly():
            line_selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.colors.get("current_line", "#2a2d2e"))
            line_selection.format.setBackground(line_color)
            line_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            line_selection.cursor = self.textCursor()
            line_selection.cursor.clearSelection()
            selections.append(line_selection)

        self.setExtraSelections(selections)
        self.line_number_area.update()       # 🔄 Redibujar margen izquierdo
        self.viewport().update()             # 🔄 Redibujar scroll marker derecho

    def line_number_area_size(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return QSize(space, 0)

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_size().width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_size().width(), cr.height()))

    def highlight_current_line(self):
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.colors.get("current_line", "#2a2d2e"))
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.setExtraSelections([selection])
        else:
            self.setExtraSelections([])

    def line_number_area_paint(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.colors.get("line_number_bg", "#1e1e1e")))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        font_metrics = QFontMetrics(self.font())

        font = QFont("Consolas", self.font().pointSize())
        painter.setFont(font)
        painter.setPen(QColor("white"))

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                color = QColor(self.colors.get("line_number_fg", "#555"))
                painter.setPen(color)
                painter.drawText(0, top, self.line_number_area.width() - 4,
                                 font_metrics.height(),
                                 Qt.AlignRight, number)

                # ✅ Dibujar barra de coincidencia si es una línea con match
                if (block_number + 1) in self.match_lines:
                    bar_color = QColor(self.colors.get("highlight_match", "#7dff64"))
                    painter.fillRect(0, top, 4, font_metrics.height(), bar_color)

                # Línea actual (donde está el cursor)
                if block_number == self.textCursor().blockNumber():
                    cursor_line_color = QColor(self.colors.get("cursor_marker", "#00ffff"))
                    painter.fillRect(0, top, 4, font_metrics.height(), cursor_line_color)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    def set_font(self, font: QFont):
        self.setFont(font)
        self.update_line_number_area_width()
        self.line_number_area.update()