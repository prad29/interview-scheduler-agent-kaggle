"""
PDF Parser

Extracts text content from PDF files using multiple fallback strategies
for maximum compatibility with different PDF formats.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing PDF libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available, using PyPDF2 only")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.debug("PyMuPDF not available (optional)")


def extract_text_with_pdfplumber(pdf_path: str) -> Optional[str]:
    """
    Extract text using pdfplumber (best for tables and complex layouts)
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    if not PDFPLUMBER_AVAILABLE:
        return None
    
    try:
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
                
                # Also try to extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        # Convert table to text
                        for row in table:
                            if row:
                                row_text = ' | '.join([str(cell) if cell else '' for cell in row])
                                text_parts.append(row_text)
        
        if text_parts:
            full_text = '\n'.join(text_parts)
            logger.info(f"pdfplumber: Extracted {len(full_text)} characters")
            return full_text
        
        return None
        
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {str(e)}")
        return None


def extract_text_with_pypdf2(pdf_path: str) -> Optional[str]:
    """
    Extract text using PyPDF2 (good for simple PDFs)
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    if not PYPDF2_AVAILABLE:
        return None
    
    try:
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"Extracted {len(page_text)} chars from page {page_num + 1}")
        
        if text_parts:
            full_text = '\n'.join(text_parts)
            logger.info(f"PyPDF2: Extracted {len(full_text)} characters")
            return full_text
        
        return None
        
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {str(e)}")
        return None


def extract_text_with_pymupdf(pdf_path: str) -> Optional[str]:
    """
    Extract text using PyMuPDF/fitz (good for OCR and images)
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    if not PYMUPDF_AVAILABLE:
        return None
    
    try:
        text_parts = []
        
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            if page_text:
                text_parts.append(page_text)
                logger.debug(f"Extracted {len(page_text)} chars from page {page_num + 1}")
        
        doc.close()
        
        if text_parts:
            full_text = '\n'.join(text_parts)
            logger.info(f"PyMuPDF: Extracted {len(full_text)} characters")
            return full_text
        
        return None
        
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {str(e)}")
        return None


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from PDF file
    
    Uses multiple extraction strategies in order of preference:
    1. pdfplumber (best for tables and complex layouts)
    2. PyMuPDF (good for images and OCR)
    3. PyPDF2 (simple fallback)
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text content
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If all extraction methods fail
    """
    # Validate file exists
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    # Try extraction methods in order of preference
    extraction_methods = [
        ("pdfplumber", extract_text_with_pdfplumber),
        ("PyMuPDF", extract_text_with_pymupdf),
        ("PyPDF2", extract_text_with_pypdf2)
    ]
    
    for method_name, extraction_func in extraction_methods:
        try:
            text = extraction_func(pdf_path)
            
            if text and len(text.strip()) > 0:
                logger.info(f"Successfully extracted text using {method_name}")
                return text.strip()
            else:
                logger.debug(f"{method_name} returned empty text")
                
        except Exception as e:
            logger.debug(f"{method_name} failed: {str(e)}")
            continue
    
    # If all methods fail
    raise Exception(
        f"Failed to extract text from PDF: {pdf_path}. "
        "All extraction methods failed. The PDF might be image-based, "
        "corrupted, or require OCR. Please install pdfplumber and PyMuPDF "
        "for better extraction support."
    )


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with PDF metadata
    """
    metadata = {
        'pages': 0,
        'author': None,
        'title': None,
        'subject': None,
        'creator': None,
        'producer': None,
        'creation_date': None
    }
    
    try:
        if PYPDF2_AVAILABLE:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata['pages'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata['author'] = pdf_reader.metadata.get('/Author')
                    metadata['title'] = pdf_reader.metadata.get('/Title')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator')
                    metadata['producer'] = pdf_reader.metadata.get('/Producer')
                    metadata['creation_date'] = pdf_reader.metadata.get('/CreationDate')
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to extract PDF metadata: {str(e)}")
        return metadata


def is_pdf_text_based(pdf_path: str) -> bool:
    """
    Check if PDF contains searchable text or is image-based
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        True if PDF contains text, False if image-based
    """
    try:
        # Try to extract text
        text = extract_text_from_pdf(pdf_path)
        
        # If we got substantial text, it's text-based
        # Use a threshold of 100 characters to account for minimal text in headers/footers
        return len(text.strip()) > 100
        
    except Exception:
        return False


# Alias for backwards compatibility
parse_pdf = extract_text_from_pdf