"""Mock configurations for file operations."""

from unittest.mock import AsyncMock, MagicMock, mock_open
from pathlib import Path
from typing import Any, Dict, Optional
import json


class MockFileManager:
    """Mock file manager for testing file operations."""

    def __init__(self):
        self.files = {}
        self.directories = set()
        self._setup_default_structure()

    def _setup_default_structure(self):
        """Setup default file structure."""
        # Create default directories
        self.directories.update(
            [
                "papers",
                "papers/source",
                "papers/translation",
                "papers/heartfelt",
                "output",
                "output/images",
                "temp",
            ]
        )

        # Create default files
        self.files["papers/source/test_paper.pdf"] = b"%PDF-1.4\nTest PDF content"
        self.files["config.json"] = json.dumps(
            {
                "claude_api_key": "test_key",
                "papers_dir": "papers",
                "output_dir": "output",
            }
        ).encode()

    def exists(self, path: str) -> bool:
        """Mock Path.exists() method."""
        path_str = str(path)
        if path_str in self.files:
            return True
        # Check if it's a directory
        return any(
            path_str == d or path_str.startswith(f"{d}/") for d in self.directories
        )

    def is_file(self, path: str) -> bool:
        """Mock Path.is_file() method."""
        return str(path) in self.files

    def is_dir(self, path: str) -> bool:
        """Mock Path.is_dir() method."""
        path_str = str(path)
        return path_str in self.directories

    def read_bytes(self, path: str) -> bytes:
        """Mock read_bytes() method."""
        if str(path) in self.files:
            return self.files[str(path)]
        raise FileNotFoundError(f"File not found: {path}")

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Mock read_text() method."""
        content = self.read_bytes(path)
        return content.decode(encoding)

    def write_bytes(self, path: str, content: bytes):
        """Mock write_bytes() method."""
        self.files[str(path)] = content

    def write_text(self, path: str, content: str, encoding: str = "utf-8"):
        """Mock write_text() method."""
        self.files[str(path)] = content.encode(encoding)

    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False):
        """Mock mkdir() method."""
        path_str = str(path)
        if not exist_ok and path_str in self.directories:
            raise FileExistsError(f"Directory exists: {path}")
        self.directories.add(path_str)

    def iterdir(self, path: str):
        """Mock iterdir() method."""
        path_str = str(path)
        files = []
        for f in self.files:
            if f.startswith(f"{path_str}/"):
                rel_path = f[len(path_str) + 1 :]
                if "/" not in rel_path:  # Direct child only
                    files.append(Path(rel_path))
        for d in self.directories:
            if d.startswith(f"{path_str}/"):
                rel_path = d[len(path_str) + 1 :]
                if "/" not in rel_path:  # Direct child only
                    files.append(Path(rel_path))
        return iter(files)

    def unlink(self, path: str):
        """Mock unlink() method."""
        if str(path) in self.files:
            del self.files[str(path)]
        else:
            raise FileNotFoundError(f"File not found: {path}")

    def rmtree(self, path: str):
        """Mock rmtree() method."""
        path_str = str(path)
        # Remove directory
        if path_str in self.directories:
            self.directories.remove(path_str)
        # Remove all files and subdirectories
        files_to_remove = [f for f in self.files if f.startswith(f"{path_str}/")]
        for f in files_to_remove:
            del self.files[f]
        dirs_to_remove = [d for d in self.directories if d.startswith(f"{path_str}/")]
        for d in dirs_to_remove:
            self.directories.remove(d)

    def getsize(self, path: str) -> int:
        """Mock getsize() method."""
        if str(path) in self.files:
            return len(self.files[str(path)])
        raise FileNotFoundError(f"File not found: {path}")

    def add_file(self, path: str, content: bytes):
        """Add a file to the mock file system."""
        self.files[str(path)] = content

    def add_text_file(self, path: str, content: str):
        """Add a text file to the mock file system."""
        self.files[str(path)] = content.encode("utf-8")


class MockAiofiles:
    """Mock aiofiles for async file operations."""

    def __init__(self, file_manager: MockFileManager):
        self.file_manager = file_manager

    async def open(self, path: str, mode: str = "r", **kwargs):
        """Mock async file open."""
        return MockAsyncFile(path, mode, self.file_manager)


class MockAsyncFile:
    """Mock async file object."""

    def __init__(self, path: str, mode: str, file_manager: MockFileManager):
        self.path = str(path)
        self.mode = mode
        self.file_manager = file_manager
        self._content = None
        self._position = 0

    async def __aenter__(self):
        """Async context manager entry."""
        if "r" in self.mode:
            if self.file_manager.exists(self.path):
                self._content = self.file_manager.read_bytes(self.path)
            else:
                raise FileNotFoundError(f"File not found: {self.path}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def read(self) -> bytes:
        """Async read method."""
        return self._content

    async def write(self, content: bytes):
        """Async write method."""
        self.file_manager.write_bytes(self.path, content)

    async def readall(self) -> bytes:
        """Async read all method."""
        return self._content


class MockAsyncFileManager:
    """Mock for async file operations in paper service."""

    def __init__(self):
        self.uploaded_files = {}
        self.processing_files = {}

    async def save_upload(
        self, filename: str, content: bytes, category: str
    ) -> Dict[str, Any]:
        """Mock saving uploaded file."""
        file_id = f"{category}_{filename}"
        self.uploaded_files[file_id] = {
            "filename": filename,
            "content": content,
            "category": category,
            "size": len(content),
            "upload_time": "2024-01-15T14:30:22Z",
        }
        return {
            "file_id": file_id,
            "success": True,
            "message": "File uploaded successfully",
        }

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Mock getting file info."""
        return self.uploaded_files.get(file_id)

    async def delete_file(self, file_id: str) -> bool:
        """Mock deleting file."""
        if file_id in self.uploaded_files:
            del self.uploaded_files[file_id]
            return True
        return False

    async def create_processing_dir(self, paper_id: str) -> str:
        """Mock creating processing directory."""
        dir_path = f"temp/{paper_id}"
        self.processing_files[paper_id] = {
            "dir": dir_path,
            "files": {},
            "status": "created",
        }
        return dir_path

    async def save_processing_result(
        self, paper_id: str, filename: str, content: bytes
    ) -> Dict[str, Any]:
        """Mock saving processing result."""
        if paper_id not in self.processing_files:
            await self.create_processing_dir(paper_id)

        self.processing_files[paper_id]["files"][filename] = content
        return {
            "paper_id": paper_id,
            "filename": filename,
            "path": f"output/{paper_id}/{filename}",
            "success": True,
        }

    async def get_processing_result(
        self, paper_id: str, filename: str
    ) -> Optional[bytes]:
        """Mock getting processing result."""
        if paper_id in self.processing_files:
            return self.processing_files[paper_id]["files"].get(filename)
        return None


# Global mock instances
mock_file_manager = MockFileManager()
mock_aiofiles = MockAiofiles(mock_file_manager)
mock_async_file_manager = MockAsyncFileManager()


def get_mock_file_manager() -> MockFileManager:
    """Get the global mock file manager instance."""
    return mock_file_manager


def get_mock_aiofiles() -> MockAiofiles:
    """Get the global mock aiofiles instance."""
    return mock_aiofiles


def get_mock_async_file_manager() -> MockAsyncFileManager:
    """Get the global mock async file manager instance."""
    return mock_async_file_manager


# Utility functions for patching
def patch_file_operations():
    """Create patches for file operations."""
    from unittest.mock import patch

    patches = []

    # Patch Path methods
    patches.append(patch("pathlib.Path.exists", side_effect=mock_file_manager.exists))
    patches.append(patch("pathlib.Path.is_file", side_effect=mock_file_manager.is_file))
    patches.append(patch("pathlib.Path.is_dir", side_effect=mock_file_manager.is_dir))
    patches.append(
        patch("pathlib.Path.read_bytes", side_effect=mock_file_manager.read_bytes)
    )
    patches.append(
        patch("pathlib.Path.write_bytes", side_effect=mock_file_manager.write_bytes)
    )
    patches.append(patch("pathlib.Path.mkdir", side_effect=mock_file_manager.mkdir))
    patches.append(patch("pathlib.Path.iterdir", side_effect=mock_file_manager.iterdir))
    patches.append(patch("pathlib.Path.unlink", side_effect=mock_file_manager.unlink))

    # Patch aiofiles
    patches.append(patch("aiofiles.open", side_effect=mock_aiofiles.open))

    # Patch os.path.getsize
    patches.append(patch("os.path.getsize", side_effect=mock_file_manager.getsize))

    return patches
