from llama_test.service.llama_test_service import LlamaTestService


class LlamaTestServiceImpl(LlamaTestService):
    def __init__(self):
        self.__llamaTestRepository = LlamaTestRepositoryImpl()

    async def chatWithLlama(self, userSendMessage):
        return await self.__llamaTestRepository.generateText(userSendMessage)

