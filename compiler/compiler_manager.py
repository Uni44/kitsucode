import os
import shutil
import subprocess
import sys
import json

def log(msg, consola=None):
    if consola:
        consola.log(msg)
    else:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'ignore').decode())  # Quita emojis

def detectar_tipo_proyecto(project_path):
    """Detecta si el proyecto es Python según su contenido"""
    for archivo in os.listdir(project_path):
        if archivo.endswith(".py") and "main" in archivo:
            return "python"
    return "desconocido"

def compilar_python(project_path, modo_dev=False, consola=None):
    log("🧠 Detectando configuración de proyecto...", consola)

    config_path = os.path.join(project_path, "project_kc.json")
    if not os.path.exists(config_path):
        log("❌ No se encontró project_kc.json.", consola)
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        main_file = os.path.join(project_path, config.get("main_file", "main.py"))
        if not os.path.exists(main_file):
            log(f"❌ No se encontró {main_file}.", consola)
            return

        pyinstaller_exe = os.path.abspath("compilers/py/pyinstaller.exe")
        if not os.path.exists(pyinstaller_exe):
            log("❌ No se encontró pyinstaller.exe en compilers/py/", consola)
            return

        py_config = config.get("pyinstaller", {})

        # Configuraciones PyInstaller
        modo = py_config.get("mode", "onedir")
        contents_dir = py_config.get("contents_directory", ".")
        show_console = py_config.get("console", False)
        icon_path = py_config.get("icon_app") or config.get("icon_app", None)
        include_folders = py_config.get("include_folders") or config.get("include_folders", [])

        args = [pyinstaller_exe, "--noconfirm", "--clean"]

        # Onefile o onedir
        if modo == "onefile":
            args.append("--onefile")
        else:
            args.append("--onedir")

        # Console o no
        if not show_console:
            args.append("--noconsole")

        # Contenido interno
        args.extend(["--contents-directory", contents_dir])

        # Icono
        if icon_path:
            args.extend(["--icon", icon_path])

        # Incluir carpetas adicionales
        for folder in include_folders:
            args.extend(["--add-data", f"{folder};{folder}"])

        # Script principal
        args.append(main_file)

        # Ejecutar PyInstaller
        subprocess.run(args, cwd=project_path, check=True)
        log(f"✅ Compilación exitosa. Proyecto compilado en la carpeta dist.", consola)

    except subprocess.CalledProcessError as e:
        log("❌ Error durante la compilación:\n" + str(e), consola)
    except Exception as e:
        log("❌ Error inesperado:\n" + str(e), consola)

def limpiar_build(project_path, consola=None):
    for folder in ["build", "dist", "__pycache__"]:
        folder_path = os.path.join(project_path, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            log(f"🧹 Carpeta eliminada: {folder_path}")

    spec_file = os.path.join(project_path, "main.spec")
    if os.path.isfile(spec_file):
        os.remove(spec_file)
        log("🧹 Archivo main.spec eliminado.")