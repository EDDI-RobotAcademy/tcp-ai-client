from enum import Enum


class UserDefinedProtocolNumber(Enum):
    # 예약된 정보 (1, 2, 11, 12, 13, 21) 을 제외하고 사용하도록 함
    TCP_TEAM_LLAMA_TEST = 3
    TCP_TEAM_OPENAI_TEST = 7

    TCP_TEAM_LLAMA_THREE_TEST = 6

    TCP_TEAM_EXTRACT_TEXT_FROM_PDF_TEST = 8

    FIRST_USER_DEFINED_FUNCTION_FOR_TEST = 5


    @classmethod
    def hasValue(cls, value):
        return any(value == item.value for item in cls)