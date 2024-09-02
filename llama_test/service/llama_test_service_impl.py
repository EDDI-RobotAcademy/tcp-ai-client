from llama_test.repository.llama_test_repository_impl import LlamaTestRepositoryImpl
from llama_test.service.llama_test_service import LlamaTestService


class LlamaTestServiceImpl(LlamaTestService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__llamaTestRepository = LlamaTestRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def chatWithLlama(self, userSendMessage):
        return self.__llamaTestRepository.generateText(userSendMessage)

