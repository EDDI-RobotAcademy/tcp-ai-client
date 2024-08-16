from pydantic import BaseModel


class LlamaRequestForm(BaseModel):
    userSendMessage: str
