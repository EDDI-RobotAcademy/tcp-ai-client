import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import boto3
import fitz
import pymupdf4llm

import torch

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


from preprocessing.repository.preprocessing_repository import PreprocessingRepository

load_dotenv()

class PreprocessingRepositoryImpl(PreprocessingRepository):
    __instance = None

    DOWNLOAD_PATH = 'download_pdfs'
    EMBEDDING_MODEL_PATH = "intfloat/multilingual-e5-base"

    if torch.cuda.is_available():
        DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        DEVICE = "cpu"
    else:
        DEVICE = "cpu"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def downloadFileFromS3(self, fileKey):
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region_name = os.getenv('AWS_REGION')
        bucket_name = os.getenv('BUCKET_NAME')

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        if not os.path.exists(os.path.join(os.getcwd(), self.DOWNLOAD_PATH)):
            os.mkdir(os.path.join(os.getcwd(), self.DOWNLOAD_PATH))

        downloadedFileName = os.path.join(os.path.join(os.getcwd(), self.DOWNLOAD_PATH), fileKey)

        # 파일 다운로드 실행
        # s3.download_file(bucket_name, fileKey, downloadedFileName)
        try:
            s3.download_file(bucket_name, fileKey, downloadedFileName)
            print(f"File downloaded to {downloadedFileName}")
            if not os.path.isfile(downloadedFileName):
                print(f"File does not exist after download: {downloadedFileName}")
                raise FileNotFoundError(f"File {downloadedFileName} not found.")
        except Exception as e:
            print(f"Failed to download file: {e}")
            raise

        print(f"File downloaded to {downloadedFileName}")

    # async def extractTextFromPDFToMarkdown(self, PDFPath):
    #     doc = fitz.open(PDFPath)
    #     text = pymupdf4llm.to_markdown(doc)
    #
    #     return text
    async def extractTextFromPDFToMarkdown(self, PDFPath):
        if not os.path.isfile(PDFPath):
            print(f"File does not exist: {PDFPath}")
            return None

        try:
            doc = fitz.open(PDFPath)
            text = pymupdf4llm.to_markdown(doc)
            return text
        except Exception as e:
            print(f"Failed to extract text from PDF: {e}")
            raise

    async def splitTextIntoDocuments(self, text, chunkSize=256, chunkOverlap=16):
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=chunkSize, chunk_overlap=chunkOverlap)
        chunkList = textSplitter.split_text(text)

        documentList = [Document(page_content=chunk) for chunk in chunkList]
        return documentList

    async def run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            try:
                result = await loop.run_in_executor(pool, func, *args)
                print(f"Function {func.__name__} executed successfully.")
                return result
            except Exception as e:
                print(f"Error executing function {func.__name__}: {e}")
                raise

    # def create_faiss_sync(self, documentList):
    #     print("Starting create_faiss_sync")
    #     print(f"device: {self.DEVICE}")
    #     embeddings = HuggingFaceEmbeddings(
    #         model_name=self.EMBEDDING_MODEL_PATH,
    #         model_kwargs={"device": self.DEVICE},
    #         # encode_kwargs={"normalize_embeddings": True}
    #     )
    #     vectorstore = FAISS.from_documents(documentList, embeddings)
    #     print("Finished create_faiss_sync")
    #     return vectorstore

    def create_faiss_sync(self, documentList):
        print("Starting create_faiss_sync")

        try:
            # HuggingFaceEmbeddings를 생성합니다.
            embeddings = HuggingFaceEmbeddings(
                model_name=self.EMBEDDING_MODEL_PATH,
                model_kwargs={"device": self.DEVICE},
                encode_kwargs={"normalize_embeddings": True}
            )

            # FAISS 인스턴스를 생성합니다.
            vectorstore = FAISS.from_documents(documentList, embeddings)
            print("Finished create_faiss_sync")
            return vectorstore

        except Exception as e:
            # 예외 발생 시 로그를 출력합니다.
            print(f"Error during FAISS creation: {e}")
            raise

    async def createFAISS(self, documentList):
        print("Starting createFAISS")
        vectorstore = await self.run_in_executor(self.create_faiss_sync, documentList)
        print("Finished createFAISS")
        return vectorstore

    async def saveFAISS(self, vectorstore, savePath="vectorstore/faiss_index"):
        if not os.path.exists(os.path.join(os.getcwd(), "vectorstore")):
            os.mkdir(os.path.join(os.getcwd(), "vectorstore"))

        vectorstore.save_local(os.path.join(os.getcwd(), savePath))

    async def loadFAISS(self, savePath="vectorstore/faiss_index"):
        embeddings = HuggingFaceEmbeddings(
            model_name=self.EMBEDDING_MODEL_PATH,
            model_kwargs={"device": self.DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        vectorstore = FAISS.load_local(os.path.join(os.getcwd(), savePath), embeddings)
        return vectorstore
