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

    main_file = os.path.join(project_path, "main.py")

    if not os.path.exists(main_file):
        log("❌ No se encontró main.py en el proyecto.", consola)
        return

    log(f"📦 Compilando {main_file} a EXE...", consola)

    # Ruta directa al ejecutable de pyinstaller
    pyinstaller_exe = os.path.abspath("compilers/py/pyinstaller.exe")

    if not os.path.exists(pyinstaller_exe):
        log("❌ No se encontró pyinstaller.exe en compilers/py/", consola)
        return
    try:
        config_path = os.path.join(project_path, "project_kc.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        main_file = config.get("main_file", "main.py")
        include_folders = config.get("include_folders", [])
        icon_path = config.get("icon_app", None)

        args = [
            pyinstaller_exe,
            "--onedir",
            "--noconfirm",  # Evita que pregunte si sobrescribe archivos
            "--clean",      # Limpia cachés anteriores
            "--contents-directory", ".",
        ]

        # Icono
        if icon_path:
            args.extend(["--icon", icon_path])

        # Incluir carpetas
        for folder in include_folders:
            args.extend(["--add-data", f"{folder};{folder}"])

        args.append(main_file)

        if modo_dev:
            subprocess.run(args, cwd=project_path, check=True)
            log("✅ Compilación exitosa en modo DEV. Proyecto compilado en la carpeta dist.", consola)
        else:
            args.append("--noconsole")
            subprocess.run(args, cwd=project_path, check=True)
            log("✅ Compilación exitosa. Proyecto compilado en la carpeta dist.", consola)
    except subprocess.CalledProcessError as e:
        log("❌ Error durante la compilación:\n" + str(e), consola)

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