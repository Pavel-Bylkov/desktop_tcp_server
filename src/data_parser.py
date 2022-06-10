import logging

module_logger = logging.getLogger("TCP-server.data_parser")


class Data:
    def __init__(self, raw: str):
        self.BBBB = ""  # - номер участника
        self.NN = ""  # - id канала
        self.time = ""  # - HH:MM:SS Часы:минуты:секунды
        self.zhq = ""  # - десятые сотые тысячные
        self.GG = ""  # - номер группы
        if raw.endswith("\r"):
            self.raw = raw.strip('\r')
            self.valid_r = True
        else:
            self.raw = raw
            self.valid_r = False
        self.error = ""
        self.logger = logging.getLogger("TCP-server.data_parser.Data")
        self.logger.debug(f"init data raw: {raw}")

    def _add_error(self, msg: str):
        self.error = f"Ошибка: {msg}"
        return False

    def _time_is_valid(self, data_time):
        if len(data_time) != 12 or '.' not in data_time:
            return False
        time, zhq = data_time.split('.')
        try:
            HH, MM, SS = [int(x) for x in time.split(':')]
            if HH > 24 or HH < 0 or MM > 60 or MM < 0 or SS > 60 or SS < 0:
                return False
            zhq = int(zhq)
            if zhq > 999 or zhq < 0:
                return False
        except Exception:
            return False
        return True

    def parser(self):
        if not self.valid_r:
            return self._add_error("Не найден «возврат каретки»")
        data = self.raw.split()
        if len(data) != 4:
            return self._add_error("Не верное количество данных")
        if len(data[0]) != 4 or not data[0].isdigit():
            return self._add_error("Не верный формат номера участника")
        self.BBBB = data[0]
        if len(data[1]) != 2:
            return self._add_error("Не верный формат id канала")
        self.NN = data[1]
        if not self._time_is_valid(data[2]):
            return self._add_error("Не верный формат времени")
        self.time, self.zhq = data[2].split('.')
        if len(data[3]) != 2 or not data[3].isdigit():
            return self._add_error("Не верный формат номера группы")
        self.GG = data[3]
        return True

    def __str__(self):
        msg = "спортсмен, нагрудный номер {} прошёл отсечку {} в {}.{}"
        return msg.format(self.BBBB, self.NN, self.time, self.zhq[0])

    def to_log(self):
        return f"{self.raw} {self.error}"
