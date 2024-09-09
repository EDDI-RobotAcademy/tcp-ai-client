from abc import abstractmethod, ABC


class OpenaiApiService(ABC):
    @abstractmethod
    def letsChat(self, *arg, **kwargs):
        pass