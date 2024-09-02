import os

from llama_three_test.repository.llama_three_repository_impl import LlamaThreeRepositoryImpl
from llama_three_test.service.llama_three_service import LlamaThreeService
from preprocessing.repository.preprocessing_repository_impl import PreprocessingRepositoryImpl


class LlamaThreeServiceImpl(LlamaThreeService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__llamaThreeRepository = LlamaThreeRepositoryImpl.getInstance()
            cls.__instance.__preprocessingRepository = PreprocessingRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def letsChat(self, userSendMessage, fileKey=None):
        print(f"service -> letsChat() userSendMessage: {userSendMessage}")
        print(f"service -> letsChat() fileKey: {fileKey}")
        text = None

        if fileKey is not None:
            DOWNLOAD_PATH = "download_pdfs"
            FILE_PATH = os.path.join(os.getcwd(), DOWNLOAD_PATH, fileKey)

            await self.__preprocessingRepository.downloadFileFromS3(fileKey)
            text = await self.__preprocessingRepository.extractTextFromPDFToMarkdown(FILE_PATH)
            print("finish to extract pdf")
            documentList = await self.__preprocessingRepository.splitTextIntoDocuments(text)
            print("finish to split text")

            vectorstore = await self.__preprocessingRepository.createFAISS(documentList)
            print("finish to create faiss")
            await self.__preprocessingRepository.saveFAISS(vectorstore)
            print("finish to save faiss")

        else:
            vectorstore = await self.__preprocessingRepository.loadFAISS()
            print("finish to load faiss")

        return await self.__llamaThreeRepository.generateText(userSendMessage, vectorstore, text)