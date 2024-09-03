import os

from dotenv import load_dotenv
from langchain import hub
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import openai

from llama_three_test.repository.llama_three_repository import LlamaThreeRepository

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class LlamaThreeRepositoryImpl(LlamaThreeRepository):
    __instance = None

    llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o-mini")
    memory = ConversationSummaryBufferMemory(llm=llm, memory_key='chat_history', return_messages=True)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateText(self, userSendMessage, vectorstore, fileKey):
        if vectorstore is None:
            template = """
            너는 사용자를 도와서 논문 요약 및 번역을 하는 어시스턴트야.
            사용자의 질문에 알맞은 대답을 해줘야 해.
            대답은 반드시 한국어로 번역해서 해줘야 해.
            대답하기 전에 스스로 검증하고 대답해.
            모르는 내용은 만들어내지말고 모른다고 대답해야 돼.
            사용자의 질문: {question}
            """

            prompt_template = PromptTemplate(
                input_variables=["question"],
                template=template
            )

            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            return {"message": chain.run(userSendMessage)}

        if "요약" not in userSendMessage:
            # conversationChain = ConversationalRetrievalChain.from_llm(
            #     llm=self.llm,
            #     chain_type="stuff",
            #     retriever=vectorstore.as_retriever(),
            #     memory=self.memory
            # )

            def format_docs(docs):
                return "\n\n".join([doc.page_content for doc in docs])

            prompt = hub.pull("godk/korean-rag")

            rag_chain = (
                {"context": vectorstore.as_retriever() | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

            # output = conversationChain({"question": userSendMessage})


            # return {"message": output["answer"]}
            return {"message": rag_chain.invoke(userSendMessage)}

        else:
            docs = PyMuPDFLoader(os.path.join(os.getcwd(), "download_pdfs", fileKey)).load()

            prompt_template = """Please summarize the sentence according to the following REQUEST.
            REQUEST:
            1. Summarize the main points in bullet points in KOREAN.
            2. Each summarized sentence must start with an emoji that fits the meaning of the each sentence.
            3. Use various emojis to make the summary more interesting.
            4. Translate the summary into Korean if it is written in English.
            5. DO NOT translate any technical terms.
            6. DO NOT include any unnecessary information.
            CONTEXT:
            {context}

            SUMMARY:"
            """
            prompt = PromptTemplate.from_template(prompt_template)

            llm_chain = LLMChain(llm=self.llm, prompt=prompt)


            # StuffDocumentsChain 정의
            stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="context")


            output = stuff_chain.invoke({"input_documents": docs})

            return {"message": output["output_text"]}
