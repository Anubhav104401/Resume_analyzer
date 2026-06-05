import io
import PyPDF2
from docx import Document

class ResumeParser:
    """Handles extraction of text from various resume file formats."""
    
    @staticmethod
    def extract_text(file_obj, filename: str) -> str:
        """
        Extracts text from an uploaded file based on its extension.
        Returns the extracted text or raises a ValueError if unsupported.
        """
        if not file_obj:
            raise ValueError("No file provided.")
            
        ext = filename.split('.')[-1].lower()
        
        try:
            if ext == 'pdf':
                return ResumeParser._extract_from_pdf(file_obj)
            elif ext in ['doc', 'docx']:
                return ResumeParser._extract_from_docx(file_obj)
            else:
                raise ValueError(f"Unsupported file format: {ext}. Please upload PDF or DOCX.")
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")

    @staticmethod
    def _extract_from_pdf(file_obj) -> str:
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            raise Exception(f"Failed to read PDF: {str(e)}")
            
        if not text.strip():
            raise Exception("PDF appears to be empty or contains only unextractable images.")
            
        return text

    @staticmethod
    def _extract_from_docx(file_obj) -> str:
        text = ""
        try:
            doc = Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise Exception(f"Failed to read DOCX: {str(e)}")
            
        if not text.strip():
            raise Exception("Document appears to be empty.")
            
        return text
