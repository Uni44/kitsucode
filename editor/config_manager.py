# editor/config_manager.py
import os
import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".unieditor_config.json")

def save_window_state(editor):
    try:
        files = [editor.tabs.widget(i).file_path for i in range(editor.tabs.count()) if hasattr(editor.tabs.widget(i), 'file_path')]
        config = {
            "size": [editor.size().width(), editor.size().height()],
            "pos": [editor.pos().x(), editor.pos().y()],
            "font_size": editor.font_size,
            "files": files,
            "project": editor.project_path
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        print("Configuración guardada.")
    except Exception as e:
        print("Error al guardar config:", e)

def restore_window_state(editor):
    if os.path.exists(CONFIG_PATH) and os.path.getsize(CONFIG_PATH) > 0:
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            
            if "size" in config:
                editor.resize(*config["size"])
            if "pos" in config:
                editor.move(*config["pos"])
            if "font_size" in config:
                editor.forze_adjust_font_size(config["font_size"])  # Asegurate de tener este método
            if "files" in config:
                for path in config["files"]:
                    editor.open_file_from_tree(path)  # Este método debería abrir archivos
            if "project" in config and config["project"]:
                editor.forze_open_project(config["project"])
            
            print("Configuración restaurada.")
        except Exception as e:
            print("Error al restaurar configuración:", e)
    else:
        print("No se encontró una configuración válida.")