from abc import abstractmethod, ABC


class LlamaThreeRepository(ABC):
    @abstractmethod
    def generateText(self, userSendMessage, vectorstore, fileKey, mainText):
        pass