import abc

DEFAULT_MESSAGE_TAG = 'SRApp'
DEFAULT_ERROR_TAG = 'SRApp - błąd'
DEFAULT_INFO_TITLE = 'SRApp'


class ILogger:

    @abc.abstractmethod
    def message(self, message: str, tag: str = DEFAULT_MESSAGE_TAG):
        pass

    @abc.abstractmethod
    def error(self, message: str, tag: str = DEFAULT_ERROR_TAG):
        pass

    @abc.abstractmethod
    def information(self, message: str, title: str = DEFAULT_INFO_TITLE):
        pass
