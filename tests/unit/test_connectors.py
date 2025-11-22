"""
Unit tests for ERP connectors.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestRESTConnector:
    """Tests for REST API connector."""

    def test_import_rest_connector(self):
        """Test that REST connector can be imported."""
        from integrations.connectors import RESTConnector
        assert RESTConnector is not None

    def test_rest_connector_initialization(self):
        """Test RESTConnector can be initialized."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(
            base_url="https://api.example.com",
            auth_token="test_token"
        )
        assert connector is not None

    def test_rest_get_request(self):
        """Test REST GET request."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(base_url="https://api.example.com")

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"data": "test"}

            result = connector.get("/endpoint")

            assert result is not None

    def test_rest_post_request(self):
        """Test REST POST request."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(base_url="https://api.example.com")

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {"id": 1}

            result = connector.post("/endpoint", data={"field": "value"})

            assert result is not None

    def test_rest_put_request(self):
        """Test REST PUT request."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(base_url="https://api.example.com")

        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 200

            result = connector.put("/endpoint/1", data={"field": "updated"})

            assert result is not None

    def test_rest_delete_request(self):
        """Test REST DELETE request."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(base_url="https://api.example.com")

        with patch('requests.delete') as mock_delete:
            mock_delete.return_value.status_code = 204

            result = connector.delete("/endpoint/1")

            assert result is not None or result is True

    def test_rest_with_authentication(self):
        """Test REST connector with authentication."""
        from integrations.connectors import RESTConnector
        connector = RESTConnector(
            base_url="https://api.example.com",
            auth_token="Bearer token123"
        )

        headers = connector.get_headers()

        assert "Authorization" in headers


class TestDatabaseConnector:
    """Tests for database connector."""

    def test_import_database_connector(self):
        """Test that database connector can be imported."""
        from integrations.connectors import DatabaseConnector
        assert DatabaseConnector is not None

    def test_database_connector_initialization(self):
        """Test DatabaseConnector can be initialized."""
        from integrations.connectors import DatabaseConnector
        connector = DatabaseConnector(
            connection_string="postgresql://user:pass@localhost/db"
        )
        assert connector is not None

    def test_database_query(self):
        """Test database query execution."""
        from integrations.connectors import DatabaseConnector
        connector = DatabaseConnector(
            connection_string="postgresql://localhost/test"
        )

        with patch.object(connector, '_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [{"id": 1}]
            mock_conn.cursor.return_value = mock_cursor

            result = connector.query("SELECT * FROM table")

            assert result is not None

    def test_database_insert(self):
        """Test database insert operation."""
        from integrations.connectors import DatabaseConnector
        connector = DatabaseConnector(
            connection_string="postgresql://localhost/test"
        )

        with patch.object(connector, '_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.lastrowid = 1
            mock_conn.cursor.return_value = mock_cursor

            result = connector.insert(
                table="documents",
                data={"name": "test.pdf", "status": "processed"}
            )

            assert result is not None

    def test_database_update(self):
        """Test database update operation."""
        from integrations.connectors import DatabaseConnector
        connector = DatabaseConnector(
            connection_string="postgresql://localhost/test"
        )

        with patch.object(connector, '_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor

            result = connector.update(
                table="documents",
                data={"status": "completed"},
                where={"id": 1}
            )

            assert result is not None


class TestSFTPConnector:
    """Tests for SFTP connector."""

    def test_import_sftp_connector(self):
        """Test that SFTP connector can be imported."""
        from integrations.connectors import SFTPConnector
        assert SFTPConnector is not None

    def test_sftp_connector_initialization(self):
        """Test SFTPConnector can be initialized."""
        from integrations.connectors import SFTPConnector
        connector = SFTPConnector(
            host="sftp.example.com",
            username="user",
            password="pass"
        )
        assert connector is not None

    def test_sftp_upload(self):
        """Test SFTP file upload."""
        from integrations.connectors import SFTPConnector
        connector = SFTPConnector(
            host="sftp.example.com",
            username="user"
        )

        with patch.object(connector, '_client') as mock_sftp:
            mock_sftp.put = MagicMock(return_value=True)

            result = connector.upload(
                local_path="/tmp/file.pdf",
                remote_path="/uploads/file.pdf"
            )

            assert result is not None

    def test_sftp_download(self):
        """Test SFTP file download."""
        from integrations.connectors import SFTPConnector
        connector = SFTPConnector(
            host="sftp.example.com",
            username="user"
        )

        with patch.object(connector, '_client') as mock_sftp:
            mock_sftp.get = MagicMock(return_value=True)

            result = connector.download(
                remote_path="/files/doc.pdf",
                local_path="/tmp/doc.pdf"
            )

            assert result is not None

    def test_sftp_list_files(self):
        """Test SFTP list files."""
        from integrations.connectors import SFTPConnector
        connector = SFTPConnector(
            host="sftp.example.com",
            username="user"
        )

        with patch.object(connector, '_client') as mock_sftp:
            mock_sftp.listdir.return_value = ["file1.pdf", "file2.pdf"]

            files = connector.list_files("/uploads")

            assert isinstance(files, list)


class TestSAPConnector:
    """Tests for SAP connector."""

    def test_import_sap_connector(self):
        """Test that SAP connector can be imported."""
        from integrations.connectors import SAPConnector
        assert SAPConnector is not None

    def test_sap_connector_initialization(self):
        """Test SAPConnector can be initialized."""
        from integrations.connectors import SAPConnector
        connector = SAPConnector(
            host="sap.example.com",
            client="100",
            user="sapuser",
            password="pass"
        )
        assert connector is not None

    def test_sap_call_rfc(self):
        """Test SAP RFC call."""
        from integrations.connectors import SAPConnector
        connector = SAPConnector(
            host="sap.example.com",
            client="100"
        )

        with patch.object(connector, '_connection') as mock_conn:
            mock_conn.call.return_value = {"RESULT": "SUCCESS"}

            result = connector.call_rfc(
                function="BAPI_DOCUMENT_CREATE",
                params={"DOC_TYPE": "INV"}
            )

            assert result is not None

    def test_sap_read_table(self):
        """Test SAP table read."""
        from integrations.connectors import SAPConnector
        connector = SAPConnector(
            host="sap.example.com",
            client="100"
        )

        with patch.object(connector, '_connection') as mock_conn:
            mock_conn.call.return_value = {
                "DATA": [{"FIELD1": "VALUE1"}]
            }

            result = connector.read_table(
                table="BKPF",
                fields=["BUKRS", "BELNR"],
                where="BUKRS = '1000'"
            )

            assert result is not None


class TestConnectorFactory:
    """Tests for connector factory."""

    def test_import_connector_factory(self):
        """Test that connector factory can be imported."""
        from integrations.connectors import ConnectorFactory
        assert ConnectorFactory is not None

    def test_create_rest_connector(self):
        """Test creating REST connector via factory."""
        from integrations.connectors import ConnectorFactory

        connector = ConnectorFactory.create(
            connector_type="rest",
            config={"base_url": "https://api.example.com"}
        )

        assert connector is not None

    def test_create_database_connector(self):
        """Test creating database connector via factory."""
        from integrations.connectors import ConnectorFactory

        connector = ConnectorFactory.create(
            connector_type="database",
            config={"connection_string": "postgresql://localhost/db"}
        )

        assert connector is not None

    def test_get_available_connectors(self):
        """Test getting list of available connectors."""
        from integrations.connectors import ConnectorFactory

        connectors = ConnectorFactory.get_available_connectors()

        assert isinstance(connectors, list)
        assert "rest" in connectors
        assert "database" in connectors
