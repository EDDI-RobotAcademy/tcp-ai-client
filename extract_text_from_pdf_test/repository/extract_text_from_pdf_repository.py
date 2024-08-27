from abc import ABC, abstractmethod


class ExtractTextFromPdfRepository(ABC):
    @abstractmethod
    def getPaperXmlData(self):
        pass

    @abstractmethod
    def xmlToList(self, xmlPaperData):
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

    @abstractmethod
    def separateMainAndReferences(self, extratedTextList):
        pass

    @abstractmethod
    def writeTxtOfSeparatedText(self, mainTextList, referencesList, paperFilePathList):
        pass