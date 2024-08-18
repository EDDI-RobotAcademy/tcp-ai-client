from transformers import AutoTokenizer
from llama_cpp import Llama

from llama_three_test.repository.llama_three_repository import LlamaThreeRepository


class LlamaThreeRepositoryImpl(LlamaThreeRepository):
    __instance = None

    tokenizer = AutoTokenizer.from_pretrained(
        "MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M")

    model = Llama(
        model_path="/Users/j213h/Downloads/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
        n_ctx=512,
        n_gpu_layers=-1
    )
    model.verbose = False  # make model silent

    systemPrompt = """
                당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 친절하고 정확하게 답변해야 합니다.
                You are a helpful AI assistant, you'll need to answer users' queries in a friendly and accurate manner.
            """

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateText(self, userSendMessage):
        messages = [
            { "role": "system", "content": f"{self.systemPrompt}" },
            { "role": "user", "content": f"{userSendMessage}" }
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        generationKwargs = {
            "max_tokens": 512,
            "stop": ["<|eot_id|>"],
            "top_p": 0.9,
            "temperature": 0.6,
            "echo": True
        }

        response = self.model(prompt, **generationKwargs)
        generatedText = response['choices'][0]['text'][len(prompt):]

        return { "generatedText": generatedText }