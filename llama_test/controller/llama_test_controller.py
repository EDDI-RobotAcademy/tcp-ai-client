from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from llama_test.controller.request_form.llama_request_form import LlamaRequestForm
from llama_test.service.llama_test_service_impl import LlamaTestServiceImpl

llamaTestRouter = APIRouter()

async def injectLlamaTestService() -> LlamaTestServiceImpl:
    return LlamaTestServiceImpl()

@llamaTestRouter.post("/llama-test-generate")
async def chatWithLlama(llamaRequestForm: LlamaRequestForm,
                        llamaTestService: LlamaTestServiceImpl=
                        Depends(injectLlamaTestService)):
    print(f"controller -> chatWithLlama()")

    generatedText = llamaTestService.chatWithLlama(llamaRequestForm.userSendMessage)

    return JSONResponse(content=generatedText, status_code=status.HTTP_200_OK)
