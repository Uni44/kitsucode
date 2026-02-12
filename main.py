from version import __version__
import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from editor.editor_window import Editor
from utils.context_menu import register_kitsucode_context_menu, is_context_menu_registered

def run_as_admin_for_registration():
    # Reejecuta como administrador con el flag
    params = ' '.join([f'"{arg}"' for arg in sys.argv if arg != "--register"])
    params += ' --register'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

def registrar_menu_contextual():
    exe_path = os.path.abspath(sys.argv[0])
    icon_path = os.path.join(os.path.dirname(__file__), "assets/favicon.ico")
    return register_kitsucode_context_menu(exe_path, icon_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Manejar registro del men√∫ contextual
    if "--register" in sys.argv:
        estado = registrar_menu_contextual()
        if estado == "registered":
            QMessageBox.information(None, "KitsuCode", "‚úÖ Men√∫ contextual registrado.")
        elif estado == "already":
            QMessageBox.information(None, "KitsuCode", "ü¶ä Ya estaba registrado.")
        else:
            QMessageBox.critical(None, "KitsuCode", "‚ùå Error al registrar el men√∫ contextual.")
        sys.exit()

    # Manejar eliminaci√≥n del men√∫ contextual
    if "--unregister" in sys.argv:
        estado = eliminar_menu_contextual()
        if estado == "deleted":
            QMessageBox.information(None, "KitsuCode", "üóëÔ∏è Men√∫ contextual eliminado correctamente.")
        elif estado == "not_found":
            QMessageBox.information(None, "KitsuCode", "‚ö†Ô∏è El men√∫ contextual ya estaba eliminado.")
        elif estado.startswith("error:"):
            QMessageBox.critical(None, "Error", f"No se pudo eliminar: {estado[7:]}")
        sys.exit()

    # Preguntar si registrar si a√∫n no est√°
    if not is_context_menu_registered():
        respuesta = QMessageBox.question(
            None,
            "Registrar KitsuCode",
            "¬øDese√°s agregar KitsuCode al men√∫ contextual del explorador?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            run_as_admin_for_registration()

    # Iniciar el editor normalmente
    window = Editor()
    window.setWindowTitle("KitsuCode " + __version__)
    window.setWindowIcon(QIcon("assets/icon.png"))
    sys.exit(app.exec())