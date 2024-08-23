import json
import os
import re


import requests
import xml.etree.ElementTree as ET
import fitz

from extract_text_from_pdf_test.repository.extract_text_from_pdf_repository import ExtractTextFromPdfRepository


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

    def XmlToList(self, xmlPaperData):
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

    def getAllPaperFilePath(self):
        folderPath = 'papers'  # 임시 폴더 생성

        fileNameList = os.listdir(folderPath)

        filePathList = [os.path.join(folderPath, fileName) for fileName in fileNameList]

        return filePathList

    def extractTextFromPdf(self, paperFilePathList):
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







