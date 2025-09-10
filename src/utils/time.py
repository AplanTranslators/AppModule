import time
from ..utils.singleton import SingletonMeta


class TimeUtils(metaclass=SingletonMeta):
    def __init__(self):
        pass

    def format_time_m_s(self, input_time):
        minutes = input_time // 60
        input_time %= 60

        if minutes > 0:
            return f"{int(minutes)} m {int(input_time)} s"
        else:
            return f"{int(input_time)} s"

    def format_time_date_h_m_s(self, input_time):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(input_time))
    
    def format_time_h_m_s(self, input_time):
        return time.strftime("%H:%M:%S", time.localtime(input_time))
