from abc import abstractmethod, ABC


class OpenaiApiRepository(ABC):
    @abstractmethod
    def generateText(self, userSendMessage, vectorstore, fileKey, mainText):
        pass