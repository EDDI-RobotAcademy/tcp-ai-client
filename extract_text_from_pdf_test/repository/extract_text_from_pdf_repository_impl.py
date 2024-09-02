import os
import re

import boto3
import requests
import xml.etree.ElementTree as ET
import fitz
from dotenv import load_dotenv

from extract_text_from_pdf_test.repository.extract_text_from_pdf_repository import ExtractTextFromPdfRepository
from pathlib import Path

class ExtractTextFromPdfRepositoryImpl(ExtractTextFromPdfRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def getPaperXmlData(self):
        url = 'http://export.arxiv.org/api/query'
        params = {
            'search_query': 'LLM',  # 주제 검색
            'start': 0,
            'max_results': 1  # 가져올 논문 개수
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # 요청이 실패할 경우 예외 발생
        return response.text

    def xmlToList(self, xmlPaperData):
        root = ET.fromstring(xmlPaperData)
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        entryList = root.findall('atom:entry', namespaces)

        paperList = []
        for entry in entryList:
            title = entry.find('atom:title', namespaces).text
            # authors = [author.find('atom:name', namespaces).text for author in entry.findall('atom:author', namespaces)]
            # summary = entry.find('atom:summary', namespaces).text
            pdf_link = entry.find('atom:link', namespaces).attrib.get('href')

            paperList.append({
                'title': title,
                # 'authors': authors,
                # 'summary': summary,
                'pdf_link': pdf_link
            })

        return paperList

    def downloadPaperPDF(self, paperList):
        for i, paper in enumerate(paperList):
            paperTitle = paper['title']
            paperTitle = ''.join(c for c in paperTitle if c.isalnum() or c in (' ', '_')).rstrip()
            fileName = f"{paperTitle}.pdf"
            filePath = os.path.join('papers', fileName)

            os.makedirs(os.path.dirname(filePath), exist_ok=True)
            pdfURL = paper['pdf_link'].replace('http://arxiv.org/abs/', 'http://arxiv.org/pdf/')
            pdfURL += '.pdf'
            response = requests.get(pdfURL)
            response.raise_for_status()  # 요청이 실패하면 예외를 발생시킴
            with open(filePath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filePath}")

    async def downloadFileFromS3(self, fileName):
        load_dotenv()

        awsAccessKeyId = os.getenv('AWS_ACCESS_KEY_ID')
        awsSecretAccessKey = os.getenv('AWS_SECRET_ACCESS_KEY')
        regionName = os.getenv('AWS_REGION')
        bucketName = os.getenv('BUCKET_NAME')

        s3 = boto3.client(
            's3',
            aws_access_key_id=awsAccessKeyId,
            aws_secret_access_key=awsSecretAccessKey,
            region_name=regionName
        )

        s3FileKey = fileName  # S3에 있는 파일 이름
        filePath = os.path.join('papers', fileName)

        print(f"fileName: {fileName}")
        s3.download_file(bucketName, s3FileKey, filePath)

        print(f"File downloaded to {filePath}")

    async def getAllPaperFilePath(self):
        folderPath = 'papers'
        fileNameList = os.listdir(folderPath)
        filePathList = [os.path.join(folderPath, fileName) for fileName in fileNameList]

        return filePathList

    async def extractTextFromPdf(self, paperFilePathList):
        extratedTextList = []
        for paperFilePath in paperFilePathList:
            extratedText = ""
            pdf_document = fitz.open(paperFilePath)

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                extratedText += page.get_text()

            extratedText = re.sub(r'\n', ' ', extratedText)
            extratedText = re.sub(r'\b-\s*', '', extratedText)
            extratedText = re.sub(r'\s+', ' ', extratedText)
            extratedTextList.append(extratedText)

        return extratedTextList

    async def separateMainAndReferences(self, extratedTextList):
        mainTextList = []
        referencesList = []
        for text in extratedTextList:
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

            mainTextList.append(mainText)
            referencesList.append(references)

        return mainTextList, referencesList

    async def writeTxtOfSeparatedText(self, mainTextList, referencesList, paperFilePathList):
        mainFolder = 'papers_main'
        referencesFolder = 'papers_references'

        # 폴더가 없으면 생성
        os.makedirs(mainFolder, exist_ok=True)
        os.makedirs(referencesFolder, exist_ok=True)

        for mainText, paperFilePath in zip(mainTextList, paperFilePathList):
            paperTitle = Path(paperFilePath).name[:-4]
            fileName = f"{paperTitle}_main.txt"
            filePath = os.path.join(mainFolder, fileName)
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(mainText)
            print(f"{fileName} 파일이 생성되었습니다.")

        for references, paperFilePath in zip(referencesList, paperFilePathList):
            paperTitle = Path(paperFilePath).name[:-4]
            fileName = f"{paperTitle}_references.txt"
            filePath = os.path.join(referencesFolder, fileName)
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(references)
            print(f"{fileName} 파일이 생성되었습니다.")