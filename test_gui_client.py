import sys
import socket
from settings import server_addr, server_port

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)

def run(user_input, log):
    if user_input == "":
        text = "Please enter a value\n"
    else:
        try:
            # Создать сокет клиента
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # подключиться к серверу
            clientSocket.connect((server_addr, server_port))
            sendData = f"{user_input}\r"
            raw = sendData.encode("utf-8")
            clientSocket.send(raw)
            recvData = clientSocket.recv(1024)
            text = "Ответ сервера: %s\n" % recvData.decode("utf-8")
            clientSocket.close()
        except Exception as e:
            text = "Ошибка сервера: %s\n" % e
    QMetaObject.invokeMethod(log,
                "append", Qt.QueuedConnection,
                Q_ARG(str, text))

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

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        label = QLabel('Test message')
        self.amount_input = QLineEdit()
        self.amount_input.setText("0007 C1 11:13:05.877 00")
        submit = QPushButton('Send', self)
        box = LogginOutput(self)

        submit.clicked.connect(lambda: self.changeLabel(box, self.amount_input))

        grid = QGridLayout()
        grid.addWidget(label, 0, 0)
        grid.addWidget(self.amount_input, 1, 0)
        grid.addWidget(submit, 1, 1)
        grid.addWidget(box, 2, 0, 5, 2)

        self.setLayout(grid)
        self.resize(350, 250)
        self.setWindowTitle('TCP test client')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def changeLabel(self, box, user_input):
        self.p = ProcessRunnable(target=run, args=(user_input.displayText(), box))
        self.p.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = App()
    sys.exit(app.exec_())