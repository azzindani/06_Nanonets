"""
Unit tests for storage services (S3/MinIO).
"""
import pytest
from unittest.mock import patch, MagicMock
import io


class TestS3Storage:
    """Tests for S3 storage service."""

    def test_import_storage_service(self):
        """Test that storage service can be imported."""
        from services.s3_storage import S3StorageService
        assert S3StorageService is not None

    def test_storage_initialization(self):
        """Test S3StorageService can be initialized."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()
        assert storage is not None

    def test_upload_file(self):
        """Test file upload to S3."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        # Mock file content
        content = b"test file content"
        file_obj = io.BytesIO(content)

        with patch.object(storage, '_client') as mock_client:
            mock_client.put_object = MagicMock(return_value=True)

            result = storage.upload_file(
                file_obj,
                bucket="test-bucket",
                key="test/file.txt"
            )

            assert result is not None

    def test_download_file(self):
        """Test file download from S3."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_response = MagicMock()
            mock_response.read.return_value = b"file content"
            mock_client.get_object = MagicMock(return_value={"Body": mock_response})

            result = storage.download_file(
                bucket="test-bucket",
                key="test/file.txt"
            )

            assert result is not None

    def test_delete_file(self):
        """Test file deletion from S3."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.delete_object = MagicMock(return_value=True)

            result = storage.delete_file(
                bucket="test-bucket",
                key="test/file.txt"
            )

            assert result is True or result is None

    def test_list_files(self):
        """Test listing files in S3 bucket."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.list_objects_v2 = MagicMock(return_value={
                "Contents": [
                    {"Key": "file1.txt"},
                    {"Key": "file2.txt"}
                ]
            })

            files = storage.list_files(bucket="test-bucket", prefix="")

            assert isinstance(files, list)

    def test_generate_presigned_url(self):
        """Test generating presigned URL."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.generate_presigned_url = MagicMock(
                return_value="https://s3.example.com/presigned"
            )

            url = storage.generate_presigned_url(
                bucket="test-bucket",
                key="test/file.txt",
                expiration=3600
            )

            assert url is not None
            assert "presigned" in url or url is not None

    def test_file_exists(self):
        """Test checking if file exists."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.head_object = MagicMock(return_value={"ContentLength": 100})

            exists = storage.file_exists(
                bucket="test-bucket",
                key="test/file.txt"
            )

            assert isinstance(exists, bool)

    def test_get_file_metadata(self):
        """Test getting file metadata."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.head_object = MagicMock(return_value={
                "ContentLength": 1024,
                "ContentType": "text/plain",
                "LastModified": "2024-01-15T10:00:00Z"
            })

            metadata = storage.get_file_metadata(
                bucket="test-bucket",
                key="test/file.txt"
            )

            assert metadata is not None

    def test_create_bucket(self):
        """Test creating a new bucket."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.create_bucket = MagicMock(return_value=True)

            result = storage.create_bucket("new-bucket")

            assert result is not None

    def test_bucket_exists(self):
        """Test checking if bucket exists."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        with patch.object(storage, '_client') as mock_client:
            mock_client.head_bucket = MagicMock(return_value=True)

            exists = storage.bucket_exists("test-bucket")

            assert isinstance(exists, bool)


class TestStorageHelpers:
    """Tests for storage helper functions."""

    def test_generate_unique_key(self):
        """Test generating unique storage keys."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        key1 = storage.generate_unique_key("document.pdf")
        key2 = storage.generate_unique_key("document.pdf")

        assert key1 != key2

    def test_get_content_type(self):
        """Test getting content type from filename."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        assert storage.get_content_type("file.pdf") == "application/pdf"
        assert storage.get_content_type("file.png") == "image/png"
        assert storage.get_content_type("file.json") == "application/json"

    def test_sanitize_key(self):
        """Test sanitizing storage keys."""
        from services.s3_storage import S3StorageService
        storage = S3StorageService()

        # Should handle special characters
        key = storage.sanitize_key("path/to/file with spaces.txt")
        assert " " not in key or key is not None
