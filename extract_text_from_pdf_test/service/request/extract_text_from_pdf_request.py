from template.request_generator.base_request import BaseRequest
from user_defined_protocol.protocol import UserDefinedProtocolNumber


class ExtractTextFromPdfRequest(BaseRequest):
    def __init__(self, parameterList=None):
        self.__protocolNumber = UserDefinedProtocolNumber.TCP_TEAM_EXTRACT_TEXT_FROM_PDF_TEST.value
        self.parameterList = parameterList if parameterList is not None else []

    def getProtocolNumber(self):
        return self.__protocolNumber

    def getParameterList(self):
        return tuple(self.parameterList)

    def toDictionary(self):
        return {
            "protocolNumber": self.__protocolNumber,
            "parameterList": self.parameterList
        }

    def __str__(self):
        return f"ExtractTextFromPdfRequest(protocolNumber={self.__protocolNumber}, parameterList={self.parameterList})"