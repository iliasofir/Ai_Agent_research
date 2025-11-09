"""
PDF Reader Tool for extracting text from PDF documents
"""
from crewai.tools import tool
import os


@tool("PDF Document Reader")
def read_pdf(pdf_path: str, max_pages: int = None) -> str:
    """
    Reads and extracts text content from PDF documents.
    Use this tool to analyze uploaded research papers and extract relevant information.
    This is especially useful for reading user-uploaded research papers.
    
    Args:
        pdf_path: Path to the PDF file to read
        max_pages: Maximum number of pages to read (default: all pages)
        
    Returns:
        Extracted text content with metadata
    """
    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at {pdf_path}"
    
    try:
        # Try pdfplumber first (better text extraction)
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_read = min(total_pages, max_pages) if max_pages else total_pages
            
            text_content = []
            for i in range(pages_to_read):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {i+1} ---\n{text}")
            
            full_text = "\n\n".join(text_content)
            
            # Add metadata
            metadata = f"PDF: {os.path.basename(pdf_path)}\n"
            metadata += f"Total Pages: {total_pages}\n"
            metadata += f"Pages Read: {pages_to_read}\n"
            metadata += f"{'='*80}\n\n"
            
            return metadata + full_text
            
    except ImportError:
        # Fallback to PyPDF2 if pdfplumber not available
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                pages_to_read = min(total_pages, max_pages) if max_pages else total_pages
                
                text_content = []
                for i in range(pages_to_read):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {i+1} ---\n{text}")
                
                full_text = "\n\n".join(text_content)
                
                metadata = f"PDF: {os.path.basename(pdf_path)}\n"
                metadata += f"Total Pages: {total_pages}\n"
                metadata += f"Pages Read: {pages_to_read}\n"
                metadata += f"{'='*80}\n\n"
                
                return metadata + full_text
                
        except Exception as fallback_error:
            return f"Error extracting text from PDF with PyPDF2: {str(fallback_error)}"
            
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


# Create a class wrapper for backward compatibility
class PDFReaderTool:
    """Wrapper class for the PDF reader tool"""
    
    def __init__(self):
        self.tool = read_pdf
    
    def _run(self, pdf_path: str, max_pages: int = None) -> str:
        """Execute the PDF reading tool"""
        return read_pdf(pdf_path, max_pages)
    
    def __call__(self):
        """Make the class callable to return the tool"""
        return read_pdf

