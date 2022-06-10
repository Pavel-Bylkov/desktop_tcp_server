import socket
from ..settings import server_addr, server_port

# Создать сокет клиента
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# подключиться к серверу
clientSocket.connect((server_addr, server_port))


def free_data():
    while True:
        # Отправить сообщение на сервер
        sendData = input("Клиент говорит:")
        if sendData == "bye":
            clientSocket.send(sendData.encode("utf-8"))  # Кодировка: преобразовать данные в двоичную форму
            clientSocket.close()
            break
        clientSocket.send(sendData.encode("utf-8"))
        recvData = clientSocket.recv(1024)
        print("Ответ сервера: %s" % (recvData.decode("utf-8")))  # Декодирование: преобразование двоичного в символ


def test_data():
    sendData = "0007 C1 11:13:05.877 00\r"
    raw = sendData.encode("utf-8")
    clientSocket.send(raw)
    recvData = clientSocket.recv(1024)
    print("Ответ сервера: %s" % (recvData.decode("utf-8")))
    clientSocket.close()


if __name__ == '__main__':
    test_data()