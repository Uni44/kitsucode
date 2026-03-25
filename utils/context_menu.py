import winreg
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
import sys
import subprocess

def register_kitsucode_context_menu(exe_path, icon_path):
    try:
        commands = [
            (r'Directory\shell\KitsuCode', "Abrir con KitsuCode"),
            (r'*\shell\KitsuCode', "Abrir con KitsuCode")
        ]

        for key_path, label in commands:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, label)
            winreg.SetValueEx(key, 'Icon', 0, winreg.REG_SZ, icon_path)

            command_key = winreg.CreateKey(key, 'command')
            winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

        return "registered"
    except Exception as e:
        print("Error al registrar:", e)
        return "error"

def is_context_menu_registered():
    try:
        key_path = r'Directory\\shell\\KitsuCode'
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path):
            return True
    except FileNotFoundError:
        return False

def registrar_menu_contextual(parent):
    reply = QMessageBox.question(parent, "Registrar menú contextual",
        "¿Deseás registrar la opción 'Abrir con KitsuCode' en el menú contextual?\nSe abrirá una ventana de permisos de administrador.",
        QMessageBox.Yes | QMessageBox.No)

    if reply == QMessageBox.Yes:
        exe_path = sys.executable  # .exe actual, sea Python o PyInstaller
        try:
            subprocess.run([
                'powershell', '-Command',
                f'Start-Process \'{exe_path}\' -ArgumentList \'--register-context\' -Verb runAs'
            ], check=True)
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"No se pudo ejecutar como administrador:\n{e}")

def eliminar_menu_contextual(parent):
    reply = QMessageBox.question(parent, "Eliminar menú contextual",
        "¿Deseás eliminar la opción 'Abrir con KitsuCode' del menú contextual?\nSe abrirá una ventana de permisos de administrador.",
        QMessageBox.Yes | QMessageBox.No)

    if reply == QMessageBox.Yes:
        exe_path = sys.executable
        try:
            subprocess.run([
                'powershell', '-Command',
                f'Start-Process \'{exe_path}\' -ArgumentList \'--unregister-context\' -Verb runAs'
            ], check=True)
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"No se pudo ejecutar como administrador:\n{e}")