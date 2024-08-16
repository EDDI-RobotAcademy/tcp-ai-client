from llama_test.repository.llama_test_repository import LlamaTestRepository
from langchain_community.llms import Ollama
from langchain import PromptTemplate



class LlamaTestRepositoryImpl(LlamaTestRepository):
    llm = Ollama(model="benedict/linkbricks-llama3.1-korean:8b", stop=["<|eot_id|>"])

    def generateText(self, userSendMessage):
        template = """
            <|begin_of_text|>
            <|start_header_id|>system<|end_header_id|>
            {system_prompt}
            <|eot_id|>
            <|start_header_id|>system<|end_header_id|>
            {user_prompt}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
        """

        system_prompt = "You are a helpful assistant. Tell me in Korean whatever I talked."
        user_prompt = userSendMessage

        prompt = PromptTemplate(
            input_variables=["system_prompt", "user_prompt"],
            template=template
        )

        response = self.llm(prompt.format(system_prompt=system_prompt, user_prompt=user_prompt))

        return response