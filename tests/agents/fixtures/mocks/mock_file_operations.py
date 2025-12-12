"""Mock configurations for file operations."""

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any


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
        """Mock exists() method for direct calls to MockFileManager."""
        path_str = str(path)
        if path_str in self.files:
            return True
        # Check if it's a directory
        return any(
            path_str == d or path_str.startswith(f"{d}/") for d in self.directories
        )

    def exists_path(self) -> bool:
        """Mock exists() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        if path_str in mock_file_manager.files:
            return True
        # Check if it's a directory
        return any(
            path_str == d or path_str.startswith(f"{d}/")
            for d in mock_file_manager.directories
        )

    def is_file(self, path: str) -> bool:
        """Mock is_file() method for direct calls to MockFileManager."""
        return str(path) in self.files

    def is_file_path(self) -> bool:
        """Mock is_file() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        return str(self) in mock_file_manager.files

    def is_dir(self, path: str) -> bool:
        """Mock is_dir() method for direct calls to MockFileManager."""
        path_str = str(path)
        return path_str in self.directories

    def is_dir_path(self) -> bool:
        """Mock is_dir() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        return path_str in mock_file_manager.directories

    def read_bytes(self, path: str) -> bytes:
        """Mock read_bytes() method for direct calls to MockFileManager."""
        if str(path) in self.files:
            return self.files[str(path)]
        raise FileNotFoundError(f"File not found: {path}")

    def read_bytes_path(self) -> bytes:
        """Mock read_bytes() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        if path_str in mock_file_manager.files:
            return mock_file_manager.files[path_str]
        raise FileNotFoundError(f"File not found: {self}")

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Mock read_text() method."""
        content = self.read_bytes(path)
        return content.decode(encoding)

    def write_bytes(self, path: str, content: bytes):
        """Mock write_bytes() method for direct calls to MockFileManager."""
        self.files[str(path)] = content

    def write_bytes_path(self, content: bytes):
        """Mock write_bytes() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        mock_file_manager.files[str(self)] = content

    def write_text(self, path: str, content: str, encoding: str = "utf-8"):
        """Mock write_text() method."""
        self.files[str(path)] = content.encode(encoding)

    def mkdir(self, path=None, parents: bool = False, exist_ok: bool = False):
        """Mock mkdir() method for direct calls to MockFileManager."""
        if path is None:
            # Called without path argument
            path_str = str(self)
        else:
            # Called with path argument
            path_str = str(path)

        if not exist_ok and path_str in self.directories:
            raise FileExistsError(f"Directory exists: {path}")
        self.directories.add(path_str)

    def mkdir_path(self, parents: bool = False, exist_ok: bool = False, **kwargs):
        """Mock mkdir() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        if not exist_ok and path_str in mock_file_manager.directories:
            raise FileExistsError(f"Directory exists: {self}")
        mock_file_manager.directories.add(path_str)

    def iterdir(self, path: str):
        """Mock iterdir() method for direct calls to MockFileManager."""
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

    def iterdir_path(self):
        """Mock iterdir() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        files = []
        for f in mock_file_manager.files:
            if f.startswith(f"{path_str}/"):
                rel_path = f[len(path_str) + 1 :]
                if "/" not in rel_path:  # Direct child only
                    files.append(Path(rel_path))
        for d in mock_file_manager.directories:
            if d.startswith(f"{path_str}/"):
                rel_path = d[len(path_str) + 1 :]
                if "/" not in rel_path:  # Direct child only
                    files.append(Path(rel_path))
        return iter(files)

    def unlink(self, path: str):
        """Mock unlink() method for direct calls to MockFileManager."""
        if str(path) in self.files:
            del self.files[str(path)]
        else:
            raise FileNotFoundError(f"File not found: {path}")

    def unlink_path(self):
        """Mock unlink() method for pathlib.Path."""
        # When called as a bound method, self is the Path object
        path_str = str(self)
        if path_str in mock_file_manager.files:
            del mock_file_manager.files[path_str]
        else:
            raise FileNotFoundError(f"File not found: {self}")

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


# Create a global mock open function
def mock_open_builtins(path, mode="r", **kwargs):
    """Mock built-in open() function."""
    return MockFile(path, mode, mock_file_manager)


def mock_copyfileobj(fsrc, fdst, length=16 * 1024):
    """Mock shutil.copyfileobj function."""
    # Read all data from source and write to destination
    if hasattr(fsrc, "read"):
        content = fsrc.read()
    else:
        # Handle file-like objects that might not have read method
        content = fsrc

    if hasattr(fdst, "write"):
        fdst.write(content)
    else:
        # Handle string path destination
        mock_file_manager.write_bytes(fdst, content)


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


class MockFile:
    """Mock file object for built-in open() function."""

    def __init__(self, path: str, mode: str, file_manager: MockFileManager):
        self.path = str(path)
        self.mode = mode
        self.file_manager = file_manager
        self._content = None
        self._position = 0

    def __enter__(self):
        """Context manager entry."""
        if "r" in self.mode:
            if self.file_manager.exists(self.path):
                self._content = self.file_manager.read_bytes(self.path)
            else:
                raise FileNotFoundError(f"File not found: {self.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if "w" in self.mode or "a" in self.mode:
            # If we have content written, save it
            if hasattr(self, "_written_content"):
                self.file_manager.write_bytes(self.path, self._written_content)

    def read(self, size: int = -1) -> bytes:
        """Read method."""
        if size == -1:
            return self._content[self._position :]
        else:
            result = self._content[self._position : self._position + size]
            self._position += size
            return result

    def write(self, content: bytes):
        """Write method."""
        if not hasattr(self, "_written_content"):
            self._written_content = b""
        self._written_content += content

    def readall(self) -> bytes:
        """Read all method."""
        return self._content


class MockAsyncFileManager:
    """Mock for async file operations in paper service."""

    def __init__(self):
        self.uploaded_files = {}
        self.processing_files = {}

    async def save_upload(
        self, filename: str, content: bytes, category: str
    ) -> dict[str, Any]:
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

    async def get_file(self, file_id: str) -> dict[str, Any] | None:
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
    ) -> dict[str, Any]:
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

    async def get_processing_result(self, paper_id: str, filename: str) -> bytes | None:
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
class FileOperationsPatcher:
    """Context manager for patching file operations."""

    def __init__(self, custom_file_manager=None, custom_aiofiles=None):
        """Initialize the patcher with optional custom mocks."""
        self.file_manager = custom_file_manager or mock_file_manager
        self.aiofiles = custom_aiofiles or mock_aiofiles
        self.patches = []
        self.patched = False

    def __enter__(self):
        """Enter the context and apply all patches."""
        from unittest.mock import patch

        if self.patched:
            raise RuntimeError("Patcher already in use")

        # Patch Path methods
        self.patches.append(
            patch("pathlib.Path.exists", side_effect=self.file_manager.exists_path)
        )
        self.patches.append(
            patch("pathlib.Path.is_file", side_effect=self.file_manager.is_file_path)
        )
        self.patches.append(
            patch("pathlib.Path.is_dir", side_effect=self.file_manager.is_dir_path)
        )
        self.patches.append(
            patch(
                "pathlib.Path.read_bytes", side_effect=self.file_manager.read_bytes_path
            )
        )
        self.patches.append(
            patch(
                "pathlib.Path.write_bytes",
                side_effect=self.file_manager.write_bytes_path,
            )
        )
        self.patches.append(
            patch("pathlib.Path.mkdir", side_effect=self.file_manager.mkdir_path)
        )
        self.patches.append(
            patch("pathlib.Path.iterdir", side_effect=self.file_manager.iterdir_path)
        )
        self.patches.append(
            patch("pathlib.Path.unlink", side_effect=self.file_manager.unlink_path)
        )

        # Patch aiofiles
        self.patches.append(patch("aiofiles.open", side_effect=self.aiofiles.open))

        # Patch built-in open
        self.patches.append(patch("builtins.open", side_effect=mock_open_builtins))

        # Patch shutil.copyfileobj
        self.patches.append(patch("shutil.copyfileobj", side_effect=mock_copyfileobj))

        # Patch os.path.getsize
        self.patches.append(
            patch("os.path.getsize", side_effect=self.file_manager.getsize)
        )

        # Start all patches
        for p in self.patches:
            p.start()

        self.patched = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and remove all patches."""
        if not self.patched:
            return

        # Stop all patches in reverse order
        for p in reversed(self.patches):
            p.stop()

        self.patches.clear()
        self.patched = False


def patch_file_operations(custom_file_manager=None, custom_aiofiles=None):
    """Create a context manager for patching file operations.

    Args:
        custom_file_manager: Optional custom MockFileManager instance
        custom_aiofiles: Optional custom MockAiofiles instance

    Returns:
        FileOperationsPatcher context manager instance
    """
    return FileOperationsPatcher(custom_file_manager, custom_aiofiles)
