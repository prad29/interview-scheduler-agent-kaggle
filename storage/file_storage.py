"""
File storage management for resumes and documents

This module handles file upload, storage, retrieval, and deletion operations
for resumes, job descriptions, and other documents.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import mimetypes
import logging

from config import config

logger = logging.getLogger(__name__)


class FileStorage:
    """Handle file storage operations"""
    
    # Allowed file extensions
    ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    
    # Maximum file sizes (in bytes)
    MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB
    
    def __init__(self, base_path: str):
        """
        Initialize file storage
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.resumes_path = self.base_path / 'resumes'
        self.documents_path = self.base_path / 'documents'
        self.temp_path = self.base_path / 'temp'
        self.archived_path = self.base_path / 'archived'
        
        for path in [self.resumes_path, self.documents_path, self.temp_path, self.archived_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"File storage initialized at: {self.base_path}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of file hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _validate_file(
        self,
        file_path: Path,
        allowed_extensions: set,
        max_size: int
    ) -> tuple[bool, Optional[str]]:
        """
        Validate file extension and size
        
        Args:
            file_path: Path to file
            allowed_extensions: Set of allowed extensions
            max_size: Maximum file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        if file_path.suffix.lower() not in allowed_extensions:
            return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.1f} MB"
        
        return True, None
    
    def _generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """
        Generate unique filename with timestamp
        
        Args:
            original_filename: Original filename
            prefix: Optional prefix for filename
            
        Returns:
            Unique filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        name = Path(original_filename).stem
        ext = Path(original_filename).suffix
        
        # Clean filename (remove special characters)
        name = "".join(c for c in name if c.isalnum() or c in ('-', '_', ' '))
        name = name.replace(' ', '_')
        
        if prefix:
            return f"{prefix}_{timestamp}_{name}{ext}"
        else:
            return f"{timestamp}_{name}{ext}"
    
    def save_resume(
        self,
        source_path: str,
        candidate_id: Optional[str] = None,
        original_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save resume file to storage
        
        Args:
            source_path: Path to source file
            candidate_id: Optional candidate ID for organizing files
            original_filename: Original filename if different from source
            
        Returns:
            Dictionary with file information
        """
        source = Path(source_path)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Validate file
        is_valid, error = self._validate_file(
            source,
            self.ALLOWED_RESUME_EXTENSIONS,
            self.MAX_RESUME_SIZE
        )
        
        if not is_valid:
            raise ValueError(error)
        
        # Generate unique filename
        original_name = original_filename or source.name
        prefix = f"candidate_{candidate_id}" if candidate_id else "resume"
        unique_filename = self._generate_unique_filename(original_name, prefix)
        
        # Create candidate subdirectory if ID provided
        if candidate_id:
            dest_dir = self.resumes_path / candidate_id
            dest_dir.mkdir(parents=True, exist_ok=True)
        else:
            dest_dir = self.resumes_path
        
        dest_path = dest_dir / unique_filename
        
        # Copy file
        try:
            shutil.copy2(source, dest_path)
            logger.info(f"Resume saved: {dest_path}")
            
            # Calculate file hash for integrity checking
            file_hash = self._get_file_hash(dest_path)
            
            return {
                'success': True,
                'file_path': str(dest_path),
                'relative_path': str(dest_path.relative_to(self.base_path)),
                'filename': unique_filename,
                'original_filename': original_name,
                'size_bytes': dest_path.stat().st_size,
                'mime_type': mimetypes.guess_type(str(dest_path))[0],
                'file_hash': file_hash,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            raise
    
    def save_document(
        self,
        source_path: str,
        document_type: str = 'general',
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save document file to storage
        
        Args:
            source_path: Path to source file
            document_type: Type of document (job_description, policy, etc.)
            job_id: Optional job ID for organizing files
            
        Returns:
            Dictionary with file information
        """
        source = Path(source_path)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Validate file
        is_valid, error = self._validate_file(
            source,
            self.ALLOWED_DOCUMENT_EXTENSIONS,
            self.MAX_DOCUMENT_SIZE
        )
        
        if not is_valid:
            raise ValueError(error)
        
        # Generate unique filename
        prefix = f"{document_type}_{job_id}" if job_id else document_type
        unique_filename = self._generate_unique_filename(source.name, prefix)
        
        # Create subdirectory for document type
        dest_dir = self.documents_path / document_type
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        if job_id:
            dest_dir = dest_dir / job_id
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_dir / unique_filename
        
        # Copy file
        try:
            shutil.copy2(source, dest_path)
            logger.info(f"Document saved: {dest_path}")
            
            return {
                'success': True,
                'file_path': str(dest_path),
                'relative_path': str(dest_path.relative_to(self.base_path)),
                'filename': unique_filename,
                'original_filename': source.name,
                'size_bytes': dest_path.stat().st_size,
                'mime_type': mimetypes.guess_type(str(dest_path))[0],
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
    
    def get_file(self, file_path: str) -> Optional[Path]:
        """
        Get file path if it exists
        
        Args:
            file_path: Relative or absolute file path
            
        Returns:
            Path object if file exists, None otherwise
        """
        path = Path(file_path)
        
        # If relative path, make it relative to base_path
        if not path.is_absolute():
            path = self.base_path / path
        
        if path.exists() and path.is_file():
            return path
        
        return None
    
    def delete_file(self, file_path: str, archive: bool = True) -> bool:
        """
        Delete or archive a file
        
        Args:
            file_path: Path to file to delete
            archive: If True, move to archive instead of deleting
            
        Returns:
            True if successful, False otherwise
        """
        path = self.get_file(file_path)
        
        if not path:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        try:
            if archive:
                # Move to archive
                archive_path = self.archived_path / path.name
                shutil.move(str(path), str(archive_path))
                logger.info(f"File archived: {archive_path}")
            else:
                # Permanent delete
                path.unlink()
                logger.info(f"File deleted: {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def list_files(
        self,
        directory: str = 'resumes',
        extension: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in a directory
        
        Args:
            directory: Directory to list (resumes, documents, etc.)
            extension: Optional filter by extension
            
        Returns:
            List of file information dictionaries
        """
        dir_map = {
            'resumes': self.resumes_path,
            'documents': self.documents_path,
            'temp': self.temp_path,
            'archived': self.archived_path
        }
        
        dir_path = dir_map.get(directory, self.base_path / directory)
        
        if not dir_path.exists():
            return []
        
        files = []
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                if extension and file_path.suffix.lower() != extension.lower():
                    continue
                
                files.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'relative_path': str(file_path.relative_to(self.base_path)),
                    'size_bytes': file_path.stat().st_size,
                    'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    'extension': file_path.suffix
                })
        
        return files
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage statistics
        """
        def get_dir_size(path: Path) -> int:
            """Calculate total size of directory"""
            total = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total
        
        def count_files(path: Path) -> int:
            """Count files in directory"""
            return sum(1 for f in path.rglob('*') if f.is_file())
        
        return {
            'base_path': str(self.base_path),
            'resumes': {
                'count': count_files(self.resumes_path),
                'size_bytes': get_dir_size(self.resumes_path),
                'size_mb': get_dir_size(self.resumes_path) / (1024 * 1024)
            },
            'documents': {
                'count': count_files(self.documents_path),
                'size_bytes': get_dir_size(self.documents_path),
                'size_mb': get_dir_size(self.documents_path) / (1024 * 1024)
            },
            'archived': {
                'count': count_files(self.archived_path),
                'size_bytes': get_dir_size(self.archived_path),
                'size_mb': get_dir_size(self.archived_path) / (1024 * 1024)
            },
            'total': {
                'count': count_files(self.base_path),
                'size_bytes': get_dir_size(self.base_path),
                'size_mb': get_dir_size(self.base_path) / (1024 * 1024)
            }
        }
    
    def cleanup_temp_files(self, older_than_days: int = 7) -> int:
        """
        Clean up temporary files older than specified days
        
        Args:
            older_than_days: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.temp_path.rglob('*'):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted temp file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting temp file {file_path}: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} temporary files")
        return deleted_count


# Global file storage instance
_file_storage_instance: Optional[FileStorage] = None

def get_file_storage() -> FileStorage:
    """
    Get or create file storage instance (singleton pattern)
    
    Returns:
        FileStorage instance
    """
    global _file_storage_instance
    
    if _file_storage_instance is None:
        _file_storage_instance = FileStorage(config.RESUME_STORAGE_PATH)
    
    return _file_storage_instance