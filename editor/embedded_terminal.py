import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLineEdit
)
from PySide6.QtCore import QProcess, Slot

class EmbeddedTerminal(QWidget):
    def __init__(self, project_path=None, main_file="main.py"):
        super().__init__()
        self.project_path = project_path
        self.main_file = main_file
        self.process = QProcess()

        # Consola de salida
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: black; color: lime; font-family: Consolas;")
        self.output.setFontPointSize(12)

        # Controles
        self.run_button = QPushButton("▶ Ejecutar")
        self.stop_button = QPushButton("⛔ Detener")
        self.clear_button = QPushButton("🧹 Limpiar")
        self.toggle_button = QPushButton("▼ Minimizar")

        # Entrada de texto para input()
        self.input_line = QLineEdit()
        self.send_input_button = QPushButton("💬 Enviar")

        self.input_line.setPlaceholderText("Escribir entrada para el script...")
        self.input_line.setStyleSheet("background-color: #222; color: white; font-family: Consolas;")

        # Conexiones
        self.run_button.clicked.connect(self.run_script)
        self.stop_button.clicked.connect(self.stop_script)
        self.clear_button.clicked.connect(self.output.clear)
        self.toggle_button.clicked.connect(self.toggle_terminal)
        self.send_input_button.clicked.connect(self.send_input)

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_finished)

        # Layouts
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.toggle_button)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_input_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.output)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        # Empezar minimizada
        self.output.hide()
        self.input_line.hide()
        self.send_input_button.hide()
        self.toggle_button.setText("▲ Mostrar")

    # En tu clase EmbeddedTerminal
    def log(self, text):
        self.output.append(text)  # o insertPlainText(text) si no querés formateo HTML

    def set_project_path(self, project_path):
        self.project_path = project_path
        # Si es necesario, actualizar la terminal con la nueva ruta
        self.update_terminal_path()

    def update_terminal_path(self):
        if self.project_path:
            # Actualiza la terminal con la nueva ruta, dependiendo de la lógica que tengas
            pass

    @Slot()
    def run_script(self):
        if self.process.state() != QProcess.NotRunning:
            self.output.append("Ya se está ejecutando un script.")
            return
        script_path = f"{self.project_path}/{self.main_file}"
        self.output.append(f"Ejecutando: python {script_path}")
        self.process.setWorkingDirectory(self.project_path)
        self.process.start("python", [script_path])

    @Slot()
    def stop_script(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.output.append("Proceso detenido manualmente.")

    @Slot()
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.output.append(data)

    @Slot()
    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.output.append(f"<span style='color: red'>{data}</span>")

    @Slot()
    def on_finished(self):
        self.output.append("Ejecución finalizada.")

    @Slot()
    def toggle_terminal(self):
        is_visible = self.output.isVisible()
        self.output.setVisible(not is_visible)
        self.input_line.setVisible(not is_visible)
        self.send_input_button.setVisible(not is_visible)
        self.toggle_button.setText("▼ Minimizar" if not is_visible else "▲ Mostrar")

    @Slot()
    def send_input(self):
        text = self.input_line.text()
        if text:
            self.process.write((text + "\n").encode("utf-8"))
            self.input_line.clear()

    def run_command(self, command):
        if self.process.state() == QProcess.Running:
            self.process.write((command + "\n").encode("utf-8"))
        else:
            self.process.start("cmd")
            self.process.write((command + "\n").encode("utf-8"))