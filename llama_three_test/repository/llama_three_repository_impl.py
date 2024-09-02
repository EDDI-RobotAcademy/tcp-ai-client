import os

import numpy as np
import torch
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core import documents
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel, pipeline
from llama_cpp import Llama

from llama_three_test.repository.llama_three_repository import LlamaThreeRepository


class LlamaThreeRepositoryImpl(LlamaThreeRepository):
    __instance = None

    currentPath = os.getcwd()
    print(f"currentPath: {currentPath}")

    modelPath = os.path.join(currentPath, "models", "llama-3-Korean-Bllossom-8B-Q4_K_M.gguf")

    tokenizer = AutoTokenizer.from_pretrained("MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M")
    model = Llama(
        model_path=modelPath,
        n_ctx=1024,
        n_gpu_layers=-1
    )
    model.verbose = False  # make model silent

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateText(self, userSendMessage, vectorstore, context):
        # messages = [
        #     { "role": "system", "content": f"{self.systemPrompt}" },
        #     { "role": "user", "content": f"{userSendMessage}" }
        # ]
        #
        # prompt = self.tokenizer.apply_chat_template(
        #     messages,
        #     tokenize=False,
        #     add_generation_prompt=True
        # )
        #
        # generationKwargs = {
        #     "max_tokens": 512,
        #     "stop": ["<|eot_id|>"],
        #     "top_p": 0.9,
        #     "temperature": 0.6,
        #     "echo": True
        # }
        #
        # response = self.model(prompt, **generationKwargs)
        # generatedText = response['choices'][0]['text'][len(prompt):]
        #
        # return { "generatedText": generatedText }

        if context is None:
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            retrievedDocs = retriever.get_relevant_documents(userSendMessage)

            context = " ".join([doc.page_content for doc in retrievedDocs])
            prompt = f"""
                당신은 고급 논문 분석 AI 어시스턴트입니다. 주어진 논문과 검색된 관련 문서들을 기반으로 다음과 같은 작업을 수행해야 합니다:
    
                **문서와 Context 활용**:
                - 주어진 Context(검색된 문서들 포함)를 최대한 활용하여 질문에 대답하세요.
                - 응답에서 추가적인 설명이나 불필요한 정보는 포함하지 마세요.
                - 결과적으로, 질문에 대한 직접적이고 간결한 답변만 제공하세요.
    
                **Context**:
                {context}
    
                **질문**: {userSendMessage}
    
                **답변**:
                """

        else:
            prompt = f"""
                당신은 고급 논문 요약 AI 어시스턴트입니다. 주어진 Context를 기반으로 다음과 같은 작업을 수행해야 합니다:

                **문서 활용**:
                - 주어진 Context의 내용만 활용하세요.
                - 주어진 Context의 핵심 주제와 그 주제를 뒷받침하는 내용을 포함해야합니다.
                - 응답에서 추가적인 설명이나 불필요한 정보는 포함하지 마세요.
                - 결과적으로, 질문에 대한 직접적이고 간결한 답변만 제공하세요.
                
                **Context**: {context}
                
                **질문**: {userSendMessage}

                **답변**:
                """

        generationKwargs = {
            "max_tokens": 512,
            "top_p": 0.9,
            "temperature": 0.5,
            "stop": ["---", "**"],
        }

        output = self.model(prompt, **generationKwargs)

        return {"generatedText": output['choices'][0]['text'].strip()}