# editor/menu_manager.py
from version import __version__
from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox
from utils.context_menu import registrar_menu_contextual, eliminar_menu_contextual

def create_menu(editor):
    menu = QMenuBar()
    menu.setStyleSheet("QMenuBar { background-color: #333; color: white; font-size: 14px; }"
                       "QMenu { background-color: #444; color: white; }"
                       "QMenu::item { background-color: #555; padding: 10px; }"
                       "QMenu::item:selected { background-color: #666; }")

    # Info
    imagen_item = QMenu("KitsuCode", editor)
    imagen_item.setIcon(QIcon("assets/icon.png"))
    imagen_item.addAction(QAction("Versión " + __version__, editor, enabled=False))
    imagen_item.addAction(QAction("KitsuCode by Uni44", editor, enabled=False))
    imagen_item.addAction(QAction("Contacto: unigames44@gmail.com", editor, enabled=False))
    menu.addMenu(imagen_item)

    # Proyecto
    file_menu = QMenu("🗃 Proyecto", editor)
    new_project = QAction("🗄 Nuevo proyecto", editor)
    new_project.setShortcut("Ctrl+N")
    new_project.triggered.connect(editor.create_new_project)
    file_menu.addAction(new_project)

    open_project = QAction("🗃 Abrir proyecto", editor)
    open_project.setShortcut("Ctrl+O")
    open_project.triggered.connect(editor.open_project)
    file_menu.addAction(open_project)

    file_menu.addSeparator()
    close_but = QAction("❌ Salir", editor)
    close_but.setShortcut("Alt+F4")
    close_but.triggered.connect(editor.exit_app)
    file_menu.addAction(close_but)
    menu.addMenu(file_menu)

    # Archivo
    archivo = QMenu("📄 Archivo", editor)
    archivo.addAction(QAction("💾 Guardar", editor))
    archivo.addAction(QAction("💾 Guardar todo", editor))
    archivo.addSeparator()
    archivo.addAction(QAction("🔍 Buscar", editor))
    archivo.addSeparator()
    archivo.addAction(QAction("🔧 Formatear", editor))
    menu.addMenu(archivo)

    # Ejecutar
    run_menu = QMenu("🧪 Ejecutar", editor)

    run_current = QAction("🧪 Ejecutar proyecto", editor)
    run_current.setShortcut("F5")
    run_current.triggered.connect(editor.terminal.run_script)
    run_menu.addAction(run_current)

    stop_action = QAction("❌ Detener ejecución", editor)
    stop_action.setShortcut("Shift+F5")
    stop_action.triggered.connect(editor.terminal.stop_script)
    run_menu.addAction(stop_action)

    menu.addMenu(run_menu)

    # Compilar
    compile_menu = QMenu("🧰 Compilar", editor)

    build_exe = QAction("📦 Compilar proyecto", editor)
    build_exe.setShortcut("Ctrl+B")
    build_exe.triggered.connect(editor.compile_project)
    compile_menu.addAction(build_exe)

    build_exe = QAction("🐞 Compilar proyecto modo DEV", editor)
    build_exe.setShortcut("Ctrl+B")
    build_exe.triggered.connect(editor.dev_run_project)
    compile_menu.addAction(build_exe)

    clean_build = QAction("🧹 Limpiar carpeta", editor)
    clean_build.setShortcut("Ctrl+Shift+B")
    clean_build.triggered.connect(editor.clean_build_folders)
    compile_menu.addAction(clean_build)

    menu.addMenu(compile_menu)

    # Config
    config = QMenu("⚙️ Configuración", editor)
    config1 = QAction("🖱️ Registrar menú contextual", editor)
    config1.triggered.connect(lambda: registrar_menu_contextual(editor))
    config.addAction(config1)
    config2 = QAction("🖱️ Eliminar menú contextual", editor)
    config2.triggered.connect(lambda: eliminar_menu_contextual(editor))
    config.addAction(config2)
    menu.addMenu(config)

    return menu