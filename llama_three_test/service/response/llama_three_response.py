from user_defined_protocol.protocol import UserDefinedProtocolNumber


class LlamaThreeResponse:
    def __init__(self, responseData):
        self.protocolNumber = UserDefinedProtocolNumber.TCP_TEAM_LLAMA_THREE_TEST.value

        for key, value in responseData.items():
            setattr(self, key, value)

    @classmethod
    def fromResponse(cls, responseData):
        return cls(responseData)

    def toDictionary(self):
        return self.__dict__

    def __str__(self):
        return f"LlamaThreeResponse({self.__dict__})"