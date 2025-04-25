# project_explorer.py
import os
import shutil
from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSize, QTimer
from .utils import icon_for_file

ICON_FOLDER = "📁"

class ProjectExplorer(QTreeWidget):
    def __init__(self, file_open_callback):
        super().__init__()
        self.file_open_callback = file_open_callback
        self.setHeaderHidden(True)
        self.current_path = None
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.setIconSize(QSize(20, 20))
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.setStyleSheet("QTreeWidget::item { padding: 4px 2px; }")

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.last_snapshot = set()
        self._start_auto_refresh()

    def _start_auto_refresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_for_changes)
        self.timer.start(5000)  # cada 5 segundos

    def _snapshot(self, path):
        all_files = set()
        for root, dirs, files in os.walk(path):
            for name in files + dirs:
                full_path = os.path.join(root, name)
                try:
                    all_files.add((full_path, os.path.getmtime(full_path)))
                except Exception:
                    continue
        return all_files

    def _check_for_changes(self):
        if not self.current_path:
            return
        current_snapshot = self._snapshot(self.current_path)
        if current_snapshot != self.last_snapshot:
            self.last_snapshot = current_snapshot
            self.refresh()

    def set_terminal_widget(self, terminal_widget):
        self.terminal_widget = terminal_widget

    def load_project(self, path):
        self.clear()
        self.current_path = path
        self.last_snapshot = self._snapshot(path)
        root = QTreeWidgetItem([f"{ICON_FOLDER} {os.path.basename(path)}"])
        root.setData(0, Qt.UserRole, path)
        self.addTopLevelItem(root)
        self._add_items(path, root)
        root.setExpanded(True)

    def _add_items(self, path, parent_item):
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return

        for entry in entries:
            full_path = os.path.join(path, entry)
            display_name = entry
            item = QTreeWidgetItem([display_name])
            item.setData(0, Qt.UserRole, full_path)

            if os.path.isdir(full_path):
                item.setText(0, f"{ICON_FOLDER} {display_name}")
                parent_item.addChild(item)
                self._add_items(full_path, item)
            else:
                icon = icon_for_file(entry)
                item.setText(0, f"{icon} {display_name}")
                parent_item.addChild(item)

    def refresh(self):
        if self.current_path:
            self.load_project(self.current_path)

    def on_item_double_clicked(self, item, column):
        path = item.data(0, Qt.UserRole)
        if os.path.isfile(path):
            self.file_open_callback(path)

    def open_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return

        path = item.data(0, Qt.UserRole)
        menu = QMenu()

        create_file = menu.addAction("📄 Crear nuevo archivo")
        create_folder = menu.addAction("📁 Crear nueva carpeta")
        rename = menu.addAction("✏️ Renombrar")
        delete = menu.addAction("🗑️ Eliminar")
        menu.addSeparator()
        run_file = menu.addAction("▶️ Ejecutar archivo")

        action = menu.exec(self.viewport().mapToGlobal(position))

        if action == create_file:
            name, ok = QInputDialog.getText(self, "Nuevo archivo", "Nombre del archivo:")
            if ok and name:
                target_path = os.path.join(path if os.path.isdir(path) else os.path.dirname(path), name)
                if not os.path.exists(target_path):
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write("")
                    self.refresh()

        elif action == create_folder:
            name, ok = QInputDialog.getText(self, "Nueva carpeta", "Nombre de la carpeta:")
            if ok and name:
                target_path = os.path.join(path if os.path.isdir(path) else os.path.dirname(path), name)
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                    self.refresh()

        elif action == delete:
            confirm = QMessageBox.question(self, "Eliminar", f"¿Estás seguro de eliminar:\n{path}?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    self.refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")
        elif action == run_file:
            self.run_python_file(path)
        elif action == rename:
            if item == self.topLevelItem(0):
                QMessageBox.information(self, "No permitido", "No se puede renombrar la carpeta raíz del proyecto.")
                return

            old_path = item.data(0, Qt.UserRole)
            old_name = os.path.basename(old_path)
            new_name, ok = QInputDialog.getText(self, "Renombrar", f"Nuevo nombre para:\n{old_name}")
            if ok and new_name:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                try:
                    os.rename(old_path, new_path)
                    self.refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo renombrar:\n{e}")
            
    def run_python_file(self, path):
        if not hasattr(self, "terminal_widget"):
            return
        
        if not os.path.isfile(path):
            return
    
        if self.terminal_widget:
            ext = os.path.splitext(path)[1].lower()
    
            if ext == ".py":
                command = f'python "{path}"'
                self.terminal_widget.run_command(command)
            elif ext == ".bat":
                command = f'"{path}"'
                self.terminal_widget.run_command(command)
            else:
                QMessageBox.information(self, "Info", f"No se puede ejecutar archivos {ext}")
        else:
            QMessageBox.warning(self, "Terminal no conectada", "La terminal no está conectada.")