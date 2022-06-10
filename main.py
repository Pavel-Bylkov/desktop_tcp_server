#!.venv/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
import logging.config

import settings


from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QApplication,
                             QLabel, QGridLayout, QDesktopWidget, QWidget)
from PyQt5.QtCore import QObject, QTimer, QRunnable, QThreadPool, pyqtSlot
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import QTextCursor

from src.tcp_server import main as tcp_main, stop_server


class ProcessRunnable(QRunnable):
    def __init__(self, target, args=[]):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class LogginOutput(QTextEdit):
    def __init__(self, parent=None):
        super(LogginOutput, self).__init__(parent)

        self.setReadOnly(True)
        self.setLineWrapMode(self.NoWrap)
        self.insertPlainText("")

    @pyqtSlot(str)
    def append(self, text):
        self.moveCursor(QTextCursor.End)
        current = self.toPlainText()

        if current == "":
            self.insertPlainText(text)
        else:
            self.insertPlainText("" + text)

        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    def append_revers(self, text):
        current = self.toPlainText()

        if current == "":
            self.insertPlainText(text)
        else:
            self.insertPlainText(text + "\n")

        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

class OutputLogger(QObject):
    emit_write = Signal(str, int)

    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()

        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.start_server()
        self.log_time_changed = None

    def init_ui(self):
        label = QLabel('Server output')
        self.server_out = LogginOutput(self)
        label2 = QLabel('Server log')
        self.server_log = LogginOutput(self)

        grid = QGridLayout()
        grid.addWidget(label, 0, 0)
        grid.addWidget(self.server_out, 1, 0, 3, 2)
        grid.addWidget(label2, 4, 0)
        grid.addWidget(self.server_log, 5, 0, 3, 2)

        wid = QWidget(self)
        wid.setLayout(grid)
        self.setCentralWidget(wid)
        self.resize(650, 650)
        self.setWindowTitle('TCP server')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def append_log(self, text, severity):
        text = str(text)

        if severity == OutputLogger.Severity.ERROR:
            text = '<b>{}</b>'.format(text)

        self.server_out.append(text)

    def tick(self):
        file_path = settings.data_filename
        if (os.path.exists(file_path) and
                self.log_time_changed != os.path.getmtime(file_path)):
            with open(file_path, 'r') as file:
                data = [line for line in file][::-1]
                self.server_log.setText("".join(data))
            self.log_time_changed = os.path.getmtime(file_path)

    def start_server(self):
        self.p = ProcessRunnable(target=tcp_main)
        self.p.start()
        self.timer.start(1000)
        print('Server start!')


def main():
    dictLogConfig = {
        "version": 1,
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": settings.log_filename
            }
        },
        "loggers": {
            "TCP-server": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            }
        },
        "formatters": {
            "myFormatter": {
                "format": "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
            }
        }
    }

    logging.config.dictConfig(dictLogConfig)
    logger = logging.getLogger("TCP-server")
    app = QApplication([])

    mw = MainWindow()
    mw.show()

    app.exec()
    stop_server()
    sys.exit()


if __name__ == "__main__":
    main()