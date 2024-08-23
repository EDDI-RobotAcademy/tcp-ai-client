from abc import ABC, abstractmethod


class ExtractTextFromPdfRepository(ABC):
    @abstractmethod
    def getPaperXmlData(self):
        pass

    @abstractmethod
    def XmlToList(self, xmlPaperData):
        pass

    @abstractmethod
    def downloadPaperPDF(self, paperList):
        pass

    @abstractmethod
    def getAllPaperFilePath(self):
        pass

    @abstractmethod
    def extractTextFromPdf(self, paperFilePathList):
        pass