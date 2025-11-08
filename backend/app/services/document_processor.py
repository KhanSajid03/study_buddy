import os
from typing import List, Tuple
import PyPDF2
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """Service for processing and chunking documents"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def extract_text_from_pdf(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from PDF file
        Returns: List of tuples (text, page_number)
        """
        pages_text = []
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    if text.strip():
                        pages_text.append((text, page_num))
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

        return pages_text

    def extract_text_from_docx(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from DOCX file
        Returns: List of tuples (text, page_number)
        Note: DOCX doesn't have explicit pages, so we use paragraph count as proxy
        """
        pages_text = []
        try:
            doc = DocxDocument(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)

            # Combine all text
            text = "\n".join(full_text)
            pages_text.append((text, 1))
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

        return pages_text

    def extract_text_from_txt(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from TXT file
        Returns: List of tuples (text, page_number)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            return [(text, 1)]
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def extract_text(self, file_path: str, file_type: str) -> List[Tuple[str, int]]:
        """
        Extract text from document based on file type
        Returns: List of tuples (text, page_number)
        """
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "txt":
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def chunk_text(
        self, pages_text: List[Tuple[str, int]]
    ) -> List[Tuple[str, int, int]]:
        """
        Split text into chunks
        Args:
            pages_text: List of tuples (text, page_number)
        Returns:
            List of tuples (chunk_text, page_number, chunk_index)
        """
        chunks = []
        chunk_index = 0

        for text, page_num in pages_text:
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(text)

            for chunk_text in text_chunks:
                if chunk_text.strip():
                    chunks.append((chunk_text, page_num, chunk_index))
                    chunk_index += 1

        return chunks

    def process_document(
        self, file_path: str, file_type: str
    ) -> List[Tuple[str, int, int]]:
        """
        Process document: extract text and chunk it
        Returns: List of tuples (chunk_text, page_number, chunk_index)
        """
        # Extract text from document
        pages_text = self.extract_text(file_path, file_type)

        # Chunk the text
        chunks = self.chunk_text(pages_text)

        return chunks
