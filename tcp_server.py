import os
import platform

# from socketserver import TCPServer, BaseRequestHandler, ThreadingTCPServer
from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn

from data_parser import Data
import logging
import logging.config
import settings


# class MyBaseRequestHandler(BaseRequestHandler):
class MyBaseRequestHandler(StreamRequestHandler):
    logger = logging.getLogger("TCP-server.tcp_server.MyBaseRequestHandler")

    def handle(self):
        logger = MyBaseRequestHandler.logger
        self.addr = self.request.getpeername()
        self.server.users[self.addr[1]] = self.request
        message = f"IP {self.addr[0]}:{self.addr[1]} Connected..."
        logger.info(message)

        try:
            raw = self.request.recv(1024).decode('UTF-8', 'ignore')
            if raw:
                data = Data(raw)
                if data.parser():
                    if data.GG == '00':
                        print(data)
                    with open(settings.data_filename, "a", encoding="utf-8") as file:
                        print(data.raw, file=file)
                    back_data = ("OK\n").encode("utf-8")
                else:
                    back_data = (f"KO\n{data.to_log()}\n").encode("utf-8")
                logger.info(f'receive from {self.client_address}')
                logger.info(data.to_log())
                self.request.sendall(back_data)
            self.request.close()
        except Exception as e:
            logger.info(e)

# Исходный код: класс ThreadingTCPServer (ThreadingMixIn, TCPServer): проход
# Наследуется от ThreadingMixIn и TCPServer для достижения многопоточности
class MyThreadingTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.users = {}

class MyTCPserver:
    def __init__(self, server_addr='127.0.0.1', server_port=4423):
        self.server_address = server_addr
        self.server_port = server_port
        self.server_tuple = (self.server_address, self.server_port)

    def run(self):
        # server = TCPServer(self.server_tuple, MyBaseRequestHandler)
        server = MyThreadingTCPServer(self.server_tuple, MyBaseRequestHandler)
        server.serve_forever()


def kill_port(port):
    find_port = 'netstat -aon | findstr %s' % port
    result = os.popen(find_port)
    text = result.read()
    pid = text[-5:-1]
    find_kill = 'taskkill -f -pid %s' % pid
    os.popen(find_kill)


def stop_server():
    if platform.system() in ('Darwin', 'Linux'):
        os.system(f"lsof -ti:{settings.server_port} | xargs kill -9")
    elif platform.system() == 'Windows':
        kill_port(settings.server_port)


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
    module_logger = logging.getLogger("TCP-server.tcp_server")
    module_logger.info("TCP-server started")

    stop_server()
    myserver = MyTCPserver(server_addr=settings.server_addr,
                           server_port=settings.server_port)
    try:
        myserver.run()
    except:
        pass
    finally:
        module_logger.info("TCP-server stop")


if __name__ == '__main__':
    main()
