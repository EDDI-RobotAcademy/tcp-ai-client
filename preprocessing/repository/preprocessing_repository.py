from abc import abstractmethod, ABC


class PreprocessingRepository(ABC):
    @abstractmethod
    def downloadFileFromS3(self, fileKey):
        pass

    @abstractmethod
    def extractTextFromPDFToMarkdown(self, PDFPath):
        pass

    @abstractmethod
    def splitTextIntoDocuments(self, text, chunkSize=512, chunkOverlap=32):
        pass

    @abstractmethod
    def createFAISS(self, documentList):
        pass