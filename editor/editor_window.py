# editor/editor_window.py
import os
from PySide6.QtWidgets import QMainWindow, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSizePolicy, QMessageBox
from .editor_tab import EditorTab
from .project_explorer import ProjectExplorer
from .embedded_terminal import EmbeddedTerminal
from .toolbar_manager import create_toolbar
from .menu_manager import create_menu
from .config_manager import save_window_state, restore_window_state, CONFIG_PATH
from .utils import icon_for_file
import json
from compiler import compiler_manager
import chardet

class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_path = None
        self.font_size = 12
        self.terminal = EmbeddedTerminal()
        self.project_explorer = ProjectExplorer(self.open_file_from_tree)
        self.project_explorer.setMinimumWidth(240)
        self.project_explorer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.project_explorer.set_terminal_widget(self.terminal)

        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("QTabBar::tab { height: 20px; font-size: 16px; padding: 6px; }")

        self.toolbar = create_toolbar(self)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.project_explorer)
        content_layout.addWidget(self.tabs)
        layout.addLayout(content_layout)
        layout.addWidget(self.terminal)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setMenuBar(create_menu(self))
        restore_window_state(self)
        self.show()

    def exit_app(self):
        # Lógica para cerrar la aplicación
        reply = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def compile_project(self):
        if not self.project_path:
            QMessageBox.warning(self, "Sin proyecto", "Abrí o creá un proyecto primero.")
            return
    
        tipo = compiler_manager.detectar_tipo_proyecto(self.project_path)
        if tipo == "python":
            compiler_manager.compilar_python(self.project_path, modo_dev=False, consola=self.terminal)
        else:
            QMessageBox.warning(self, "Proyecto no compatible", "Solo se puede compilar proyectos Python por ahora.")
    
    def dev_run_project(self):
        if not self.project_path:
            QMessageBox.warning(self, "Sin proyecto", "Abrí o creá un proyecto primero.")
            return
    
        tipo = compiler_manager.detectar_tipo_proyecto(self.project_path)
        if tipo == "python":
            compiler_manager.compilar_python(self.project_path, modo_dev=True, consola=self.terminal)
        else:
            QMessageBox.warning(self, "Proyecto no compatible", "Solo se puede ejecutar proyectos Python por ahora.")
    
    def clean_build_folders(self):
        if not self.project_path:
            QMessageBox.warning(self, "Sin proyecto", "Abrí o creá un proyecto primero.")
            return
    
        compiler_manager.limpiar_build(self.project_path, consola=self.terminal)

    def create_new_project(self):
        path = QFileDialog.getExistingDirectory(self, "Elegí la ruta del proyecto")
        if not path:
            return

        name, _ = QFileDialog.getSaveFileName(self, "Nombre del proyecto", os.path.join(path, "nuevo_proyecto"))
        if not name:
            return

        os.makedirs(name, exist_ok=True)
        main_path = os.path.join(name, "main.py")
        bat_path = os.path.join(name, "start_debug.bat")

        project_info = {
            "name": name.strip(),
            "main_file": "main.py",
            "run_args": "",
            "interpreter": "python",
            "ignore_folders": ["__pycache__", "venv", ".git"],
            "version_app": "1.0.0",
            "pyinstaller": {
                "mode": "onedir",
                "contents_directory": ".",
                "console": false,
                "icon_app": null
            },
            "version": 1
        }

        with open(main_path, "w", encoding="utf-8") as f:
            f.write("# main.py\n")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write("python main.py\npause")
        with open(os.path.join(project_path, "project_kc.json"), "w", encoding="utf-8") as f:
            json.dump(project_info, f, indent=4)

        self.forze_open_project(name)
        self.close_all_tabs()

    def open_project(self, folder):
        folder = QFileDialog.getExistingDirectory(self, "Abrir proyecto")
        if not folder:
            return
        if not self.close_all_tabs():
            return  # el usuario canceló cerrar pestañas
        self.forze_open_project(folder)
        self.close_all_tabs()

    def load_project_config(self, folder):
        config_path = os.path.join(folder, "project_kc.json")
    
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.project_config = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo leer el archivo de configuración:\n{e}")
                self.project_config = {}
                return False
        else:
            resp = QMessageBox.question(
                self,
                "Proyecto sin configuración",
                "La carpeta seleccionada no contiene un archivo 'project_kc.json'.\n¿Querés crear uno ahora?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                self.project_config = {}
                return False
    
            name = os.path.basename(folder)
            project_info = {
                "name": name.strip(),
                "main_file": "main.py",
                "run_args": "",
                "interpreter": "python",
                "ignore_folders": ["__pycache__", "venv", ".git"],
                "version_app": "1.0.0",
                "pyinstaller": {
                    "mode": "onedir",
                    "contents_directory": ".",
                    "console": false,
                    "icon_app": null
                },
                "version": 1
            }
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(project_info, f, indent=4)
                self.project_config = project_info
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear el archivo de configuración:\n{e}")
                self.project_config = {}
                return False
    
        return True
            
    def forze_open_project(self, folder):
        if not self.load_project_config(folder):
            return  # cancelado por el usuario
        self.project_explorer.load_project(folder)
        self.terminal.set_project_path(folder)
        self.project_path = folder

    def new_python_file(self):
        folder = self.project_explorer.current_path
        if not folder:
            return
        name, _ = QFileDialog.getSaveFileName(self, "Nuevo archivo Python", folder, "Archivos Python (*.py)")
        if name:
            with open(name, "w", encoding="utf-8") as f:
                f.write("# nuevo archivo\n")
            self.project_explorer.refresh()

    def update_tab_title(self, tab, modified):
        index = self.tabs.indexOf(tab)
        if index != -1:
            emoji = icon_for_file(tab.file_path)
            name = os.path.basename(tab.file_path)
            title = f"✏️ {name}" if modified else f"{emoji} {name}"
            self.tabs.setTabText(index, title)

    def open_file_from_tree(self, file_path):
        try:
            for i in range(self.tabs.count()):
                if self.tabs.widget(i).file_path == file_path:
                    self.tabs.setCurrentIndex(i)
                    return

            tab = EditorTab(file_path, self.font_size)
            tab.modified_signal.connect(lambda mod, t=tab: self.update_tab_title(t, mod))  # ✅ Conectar señal
            emoji = icon_for_file(file_path)
            self.tabs.addTab(tab, f"{emoji} {os.path.basename(file_path)}")
            self.tabs.setCurrentWidget(tab)
        
        except Exception as e:
            # Aquí puedes manejar el error, por ejemplo, mostrando un mensaje de error
            QMessageBox.critical(self, "Error al abrir archivo", f"No se pudo abrir el archivo: {file_path}\nError: {str(e)}")

    def close_tab(self, index):
        tab = self.tabs.widget(index)
        if tab and tab.is_modified():
            resp = QMessageBox.question(self, "Cerrar sin guardar", f"¿Cerrar {tab.file_path} sin guardar?",
                                        QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.No:
                return
        self.tabs.removeTab(index)
        
    def close_all_tabs(self):
        for i in reversed(range(self.tabs.count())):
            self.close_tab(i)
        return True

    def save_current_file(self):
        current = self.tabs.currentWidget()
        if current:
            current.save()

    def save_all_files(self):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.save()

    def confirm_exit(self):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.is_modified():
                resp = QMessageBox.question(self, "Salir sin guardar", "Tenés archivos sin guardar. ¿Salir de todos modos?",
                                            QMessageBox.Yes | QMessageBox.No)
                return resp == QMessageBox.Yes
        return True

    def adjust_font_size(self, amount):
        self.font_size = max(8, min(48, self.font_size + amount))
        for i in range(self.tabs.count()):
            self.tabs.widget(i).set_font_size(self.font_size)
        save_window_state(self)  # <-- Agregá esto
        
    def forze_adjust_font_size(self, amount):
        self.font_size = amount
        for i in range(self.tabs.count()):
            self.tabs.widget(i).set_font_size(self.font_size)
        save_window_state(self)  # <-- Agregá esto 

    def closeEvent(self, event):
        save_window_state(self)
        if self.confirm_exit():
            event.accept()
        else:
            event.ignore()