import os
import re

import boto3
import fitz
import pymupdf4llm

import torch

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

from preprocessing.repository.preprocessing_repository import PreprocessingRepository

load_dotenv()

class PreprocessingRepositoryImpl(PreprocessingRepository):
    __instance = None

    DOWNLOAD_PATH = 'download_pdfs'
    EMBEDDING_MODEL_PATH = "intfloat/multilingual-e5-base"

    if torch.cuda.is_available():
        DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        DEVICE = "mps"
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
        s3.download_file(bucket_name, fileKey, downloadedFileName)

        print(f"File downloaded to {downloadedFileName}")

    def extractTextFromPDFToMarkdown(self, PDFPath):
        doc = fitz.open(PDFPath)
        text = pymupdf4llm.to_markdown(doc)

        return text

    def separateMainAndReferences(self, text):
        mainText = ''
        references = ''

        # "References" 키워드 검색 (대소문자 구분 없이)
        referencesKeyword = re.compile(r'\bReferences\b', re.IGNORECASE)
        referencesKeywordMatchList = list(re.finditer(referencesKeyword, text))
        textLength = len(text)

        # "References" 키워드가 있는 경우
        if referencesKeywordMatchList:
            lastMatch = referencesKeywordMatchList[-1]
            splitPoint = lastMatch.end()
            thresholdPosition = textLength * 0.60

            # References 키워드가 1번만 등장할 경우, 위치가 끝에서 40% 이내일 때만 분리
            if len(referencesKeywordMatchList) == 1:
                if splitPoint >= thresholdPosition:
                    mainText = text[:lastMatch.start()].strip()
                    references = text[splitPoint:].strip()
                else:
                    mainText = text.strip()
                    references = ""
            else:
                # References 키워드가 여러 번 등장하는 경우, 마지막으로 등장하는 위치에서 분리
                lastMatch = referencesKeywordMatchList[-1]
                splitPoint = lastMatch.end()

                textLength = len(text)
                fivePercentPosition = textLength * 0.95

                # References가 끝에서 5% 이내에 위치한 경우, 그 이전의 References 사용
                if splitPoint >= fivePercentPosition:
                    if len(referencesKeywordMatchList) > 1:
                        last_match = referencesKeywordMatchList[-2]
                        splitPoint = last_match.end()

                # References가 끝에서 40% 이내에 위치한 경우에만 참고문헌으로 간주
                if splitPoint >= thresholdPosition:
                    mainText = text[:lastMatch.start()].strip()
                    references = text[splitPoint:].strip()
                # References 위치가 40% 이내가 아니면 전체를 본문으로 간주
                else:
                    mainText = text.strip()
                    references = ""

        # References 키워드가 없는 경우
        else:
            # [숫자] 패턴 탐색
            pattern = re.compile(r'\[\d+\]')
            patternMatchList = list(pattern.finditer(text))
            predictedReferencesStart = None
            for i in range(len(patternMatchList) - 1, -1, -1):
                if patternMatchList[i].group() == '[1]':
                    predictedReferencesStart = patternMatchList[i].start()
                    break

            if predictedReferencesStart is not None:
                predictedFirstReference = predictedReferencesStart
                predictedLastReference = patternMatchList[-1].end()

                # 첫 번째 패턴 시작 위치가 텍스트 끝에서 40% 이내인지,
                # 마지막 패턴 끝 위치가 텍스트 끝에서 5% 이내인지 확인
                if (textLength - predictedFirstReference <= textLength * 0.4 and
                        textLength - predictedLastReference <= textLength * 0.05):
                    split_point = predictedFirstReference
                    mainText = text[:split_point].strip()
                    references = text[split_point:].strip()
                # [숫자] 패턴을 찾지 못한 경우, 전체를 본문으로 간주
                else:
                    mainText = text.strip()
                    references = ""
            else:
                mainText = text.strip()
                references = ""

        return mainText, references

    def splitTextIntoDocuments(self, text, chunkSize=256, chunkOverlap=16):
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=chunkSize, chunk_overlap=chunkOverlap)
        chunkList = textSplitter.split_text(text)

        documentList = [Document(page_content=chunk) for chunk in chunkList]
        return documentList

    def createFAISS(self, documentList):
        print("ready to create HuggingFaceEmbeddings!")
        embeddings = HuggingFaceEmbeddings(
            model_name=self.EMBEDDING_MODEL_PATH,
            model_kwargs={"device": self.DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        print(f"success to create HuggingFaceEmbeddings: {embeddings}")

        vectorstore = FAISS.from_documents(documentList, embeddings)
        print("success to create VectorStore")

        return vectorstore

    def saveFAISS(self, vectorstore, savePath="vectorstore/faiss_index"):
        if not os.path.exists(os.path.join(os.getcwd(), "vectorstore")):
            os.mkdir(os.path.join(os.getcwd(), "vectorstore"))

        vectorstore.save_local(os.path.join(os.getcwd(), savePath))

    def loadFAISS(self, savePath="vectorstore/faiss_index"):
        embeddings = HuggingFaceEmbeddings(
            model_name=self.EMBEDDING_MODEL_PATH,
            model_kwargs={"device": self.DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        vectorstore = FAISS.load_local(os.path.join(os.getcwd(), savePath),
                                       embeddings,
                                       allow_dangerous_deserialization=True)
        return vectorstore
