from abc import ABC, abstractmethod


class ExtractTextFromPdfService(ABC):
    @abstractmethod
    def extractTextFromPdf(self):
        pass