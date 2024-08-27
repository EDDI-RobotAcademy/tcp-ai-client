from extract_text_from_pdf_test.repository.extract_text_from_pdf_repository_impl import ExtractTextFromPdfRepositoryImpl
from extract_text_from_pdf_test.service.extract_text_from_pdf_service import ExtractTextFromPdfService


class ExtractTextFromPdfServiceImpl(ExtractTextFromPdfService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__extractTextFromPdfRepository = ExtractTextFromPdfRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def extractTextFromPdf(self):
        xmlPaperData = self.__extractTextFromPdfRepository.getPaperXmlData()
        paperList = self.__extractTextFromPdfRepository.xmlToList(xmlPaperData)
        self.__extractTextFromPdfRepository.downloadPaperPDF(paperList)

        paperFilePathList = self.__extractTextFromPdfRepository.getAllPaperFilePath()
        extractedTextFromPdfList = self.__extractTextFromPdfRepository.extractTextFromPdf(paperFilePathList)

        mainTextList, referencesList = (
            self.__extractTextFromPdfRepository.separateMainAndReferences(extractedTextFromPdfList))
        self.__extractTextFromPdfRepository.writeTxtOfSeparatedText(
            mainTextList, referencesList, paperFilePathList)
