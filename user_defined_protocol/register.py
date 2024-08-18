import os
import sys

from first_user_defined_function_domain.service.fudf_service_impl import FudfServiceImpl
from first_user_defined_function_domain.service.request.fudf_just_for_test_request import FudfJustForTestRequest
from first_user_defined_function_domain.service.response.fudf_just_for_test_response import FudfJustForTestResponse
from llama_test.service.llama_test_service_impl import LlamaTestServiceImpl
from llama_test.service.request.llama_test_request import LlamaTestRequest
from llama_test.service.response.llama_test_response import LlamaTestResponse
from llama_three_test.service.llama_three_service_impl import LlamaThreeServiceImpl
from llama_three_test.service.request.llama_three_request import LlamaThreeRequest
from llama_three_test.service.response.llama_three_response import LlamaThreeResponse
from openai_api_test.service.openai_api_test_service_impl import OpenaiApiTestServiceImpl
from openai_api_test.service.request.openai_api_test_request import OpenaiApiTestRequest
from openai_api_test.service.response.openai_api_test_response import OpenaiApiTestResponse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

from user_defined_protocol.protocol import UserDefinedProtocolNumber


class UserDefinedProtocolRegister:

    @staticmethod
    def registerDefaultUserDefinedProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        firstUserDefinedFunctionService = FudfServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.FIRST_USER_DEFINED_FUNCTION_FOR_TEST,
            FudfJustForTestRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.FIRST_USER_DEFINED_FUNCTION_FOR_TEST,
            FudfJustForTestResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.FIRST_USER_DEFINED_FUNCTION_FOR_TEST,
            firstUserDefinedFunctionService.justForTest
        )

    @staticmethod
    def registerLlamaTestProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        llamaTestService = LlamaTestServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_TEST,
            LlamaTestRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_TEST,
            LlamaTestResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_TEST,
            llamaTestService.chatWithLlama
        )

    @staticmethod
    def registerOpenaiApiTestProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        openaiApiTestService = OpenaiApiTestServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.TCP_TEAM_OPENAI_TEST,
            OpenaiApiTestRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.TCP_TEAM_OPENAI_TEST,
            OpenaiApiTestResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.TCP_TEAM_OPENAI_TEST,
            openaiApiTestService.letsChat
        )

    @staticmethod
    def registerLlamaThreeTestProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        llamaThreeService = LlamaThreeServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_THREE_TEST,
            LlamaThreeRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_THREE_TEST,
            LlamaThreeResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.TCP_TEAM_LLAMA_THREE_TEST,
            llamaThreeService.letsChat
        )

    @staticmethod
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerDefaultUserDefinedProtocol()
        UserDefinedProtocolRegister.registerLlamaTestProtocol()
        UserDefinedProtocolRegister.registerOpenaiApiTestProtocol()
        UserDefinedProtocolRegister.registerLlamaThreeTestProtocol()
