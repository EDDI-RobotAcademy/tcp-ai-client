from user_defined_protocol.protocol import UserDefinedProtocolNumber


class ExtractTextFromPdfResponse:
    def __init__(self, responseData):
        self.protocolNumber = UserDefinedProtocolNumber.TCP_TEAM_EXTRACT_TEXT_FROM_PDF_TEST.value

        for key, value in responseData.items():
            setattr(self, key, value)

    @classmethod
    def fromResponse(cls, responseData):
        return cls(responseData)

    def toDictionary(self):
        return self.__dict__

    def __str__(self):
        return f"ExtractTextFromPdfResponse({self.__dict__})"