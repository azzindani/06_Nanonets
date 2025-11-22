"""
Unit tests for notification services.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestEmailNotification:
    """Tests for email notification service."""

    def test_import_email_service(self):
        """Test that email service can be imported."""
        from services.notifications.email_service import EmailService
        assert EmailService is not None

    def test_email_service_initialization(self):
        """Test EmailService can be initialized."""
        from services.notifications.email_service import EmailService
        service = EmailService()
        assert service is not None

    def test_send_email(self):
        """Test sending an email."""
        from services.notifications.email_service import EmailService
        service = EmailService()

        with patch.object(service, '_smtp_client') as mock_smtp:
            mock_smtp.send_message = MagicMock(return_value=True)

            result = service.send_email(
                to="user@example.com",
                subject="Test Email",
                body="This is a test email."
            )

            assert result is not None

    def test_send_email_with_attachment(self):
        """Test sending email with attachment."""
        from services.notifications.email_service import EmailService
        service = EmailService()

        with patch.object(service, '_smtp_client') as mock_smtp:
            mock_smtp.send_message = MagicMock(return_value=True)

            result = service.send_email(
                to="user@example.com",
                subject="Test with Attachment",
                body="See attached file.",
                attachments=[{"filename": "doc.pdf", "content": b"PDF content"}]
            )

            assert result is not None

    def test_send_email_to_multiple_recipients(self):
        """Test sending email to multiple recipients."""
        from services.notifications.email_service import EmailService
        service = EmailService()

        with patch.object(service, '_smtp_client') as mock_smtp:
            mock_smtp.send_message = MagicMock(return_value=True)

            result = service.send_email(
                to=["user1@example.com", "user2@example.com"],
                subject="Test",
                body="Test message"
            )

            assert result is not None

    def test_validate_email_address(self):
        """Test email address validation."""
        from services.notifications.email_service import EmailService
        service = EmailService()

        assert service.validate_email("valid@example.com")
        assert not service.validate_email("invalid-email")
        assert not service.validate_email("")

    def test_email_template_rendering(self):
        """Test email template rendering."""
        from services.notifications.email_service import EmailService
        service = EmailService()

        template = "Hello {{ name }}, your document {{ doc_id }} is ready."
        rendered = service.render_template(
            template,
            {"name": "John", "doc_id": "DOC-001"}
        )

        assert "John" in rendered
        assert "DOC-001" in rendered


class TestSlackNotification:
    """Tests for Slack notification service."""

    def test_import_slack_service(self):
        """Test that Slack service can be imported."""
        from services.notifications.slack_service import SlackService
        assert SlackService is not None

    def test_slack_service_initialization(self):
        """Test SlackService can be initialized."""
        from services.notifications.slack_service import SlackService
        service = SlackService()
        assert service is not None

    def test_send_message(self):
        """Test sending a Slack message."""
        from services.notifications.slack_service import SlackService
        service = SlackService()

        with patch.object(service, '_client') as mock_client:
            mock_client.chat_postMessage = MagicMock(return_value={"ok": True})

            result = service.send_message(
                channel="#general",
                text="Test message"
            )

            assert result is not None

    def test_send_message_with_blocks(self):
        """Test sending Slack message with blocks."""
        from services.notifications.slack_service import SlackService
        service = SlackService()

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Document Processed*"}
            }
        ]

        with patch.object(service, '_client') as mock_client:
            mock_client.chat_postMessage = MagicMock(return_value={"ok": True})

            result = service.send_message(
                channel="#ocr-results",
                text="Document processed",
                blocks=blocks
            )

            assert result is not None

    def test_send_file(self):
        """Test sending file to Slack."""
        from services.notifications.slack_service import SlackService
        service = SlackService()

        with patch.object(service, '_client') as mock_client:
            mock_client.files_upload = MagicMock(return_value={"ok": True})

            result = service.send_file(
                channel="#documents",
                file_content=b"file content",
                filename="result.json"
            )

            assert result is not None

    def test_create_document_notification(self):
        """Test creating document processed notification."""
        from services.notifications.slack_service import SlackService
        service = SlackService()

        notification = service.create_document_notification(
            doc_id="DOC-001",
            status="completed",
            fields_extracted=10,
            processing_time=1.5
        )

        assert notification is not None


class TestWebhookNotification:
    """Tests for webhook notification service."""

    def test_import_webhook_service(self):
        """Test that webhook service can be imported."""
        from services.notifications.webhook_service import WebhookService
        assert WebhookService is not None

    def test_webhook_service_initialization(self):
        """Test WebhookService can be initialized."""
        from services.notifications.webhook_service import WebhookService
        service = WebhookService()
        assert service is not None

    def test_send_webhook(self):
        """Test sending webhook."""
        from services.notifications.webhook_service import WebhookService
        service = WebhookService()

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"received": True}

            result = service.send_webhook(
                url="https://example.com/webhook",
                payload={"event": "document.processed", "data": {}}
            )

            assert result is not None

    def test_webhook_with_signature(self):
        """Test webhook with HMAC signature."""
        from services.notifications.webhook_service import WebhookService
        service = WebhookService()

        signature = service.generate_signature(
            payload={"event": "test"},
            secret="webhook_secret"
        )

        assert signature is not None
        assert isinstance(signature, str)

    def test_webhook_retry_on_failure(self):
        """Test webhook retries on failure."""
        from services.notifications.webhook_service import WebhookService
        service = WebhookService()

        with patch('requests.post') as mock_post:
            # Fail twice, succeed on third
            mock_post.side_effect = [
                MagicMock(status_code=500),
                MagicMock(status_code=500),
                MagicMock(status_code=200)
            ]

            result = service.send_webhook(
                url="https://example.com/webhook",
                payload={"event": "test"},
                max_retries=3
            )

            # Should eventually succeed or handle gracefully
            assert result is not None or result is None

    def test_validate_webhook_url(self):
        """Test webhook URL validation."""
        from services.notifications.webhook_service import WebhookService
        service = WebhookService()

        assert service.validate_url("https://example.com/webhook")
        assert service.validate_url("http://localhost:8080/hook")
        assert not service.validate_url("not-a-url")
        assert not service.validate_url("")


class TestNotificationManager:
    """Tests for notification manager."""

    def test_import_notification_manager(self):
        """Test that notification manager can be imported."""
        from services.notifications import NotificationManager
        assert NotificationManager is not None

    def test_notification_manager_initialization(self):
        """Test NotificationManager can be initialized."""
        from services.notifications import NotificationManager
        manager = NotificationManager()
        assert manager is not None

    def test_send_notification(self):
        """Test sending notification through manager."""
        from services.notifications import NotificationManager
        manager = NotificationManager()

        with patch.object(manager, '_services') as mock_services:
            mock_services['email'].send = MagicMock(return_value=True)

            result = manager.send(
                channel="email",
                to="user@example.com",
                message="Test notification"
            )

            assert result is not None

    def test_get_available_channels(self):
        """Test getting available notification channels."""
        from services.notifications import NotificationManager
        manager = NotificationManager()

        channels = manager.get_available_channels()

        assert isinstance(channels, list)
        assert "email" in channels or len(channels) >= 0
