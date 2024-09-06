import os
import sys

from openai_api.service.open_ai_service_impl import OpenaiApiServiceImpl
from openai_api.service.request.open_ai_request import OpenaiApiRequest
from openai_api.service.response.open_ai_response import OpenaiApiResponse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

from user_defined_protocol.protocol import UserDefinedProtocolNumber


class UserDefinedProtocolRegister:
    @staticmethod
    def registerOpenaiApiProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        openaiApiService = OpenaiApiServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.OPENAI_API,
            OpenaiApiRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.OPENAI_API,
            OpenaiApiResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.OPENAI_API,
            openaiApiService.letsChat
        )



    @staticmethod
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerOpenaiApiProtocol()

