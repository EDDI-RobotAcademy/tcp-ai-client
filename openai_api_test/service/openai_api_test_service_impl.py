from openai_api_test.repository.openai_api_test_repository_impl import OpenaiApiTestRepositoryImpl
from openai_api_test.service.openai_api_test_service import OpenaiApiTestService


class OpenaiApiTestServiceImpl(OpenaiApiTestService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__openaiApiTestRepositoryImpl = OpenaiApiTestRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def letsChat(self, userSendMessage):
        return await self.__openaiApiTestRepositoryImpl.generateText(userSendMessage)