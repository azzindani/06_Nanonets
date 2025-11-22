"""
Test API endpoints and middleware.

Run with: python -m api.test_api
"""
import sys
import time
from datetime import datetime


def test_auth_middleware():
    """Test authentication middleware."""
    print("\n[1/4] Testing Auth Middleware...")
    try:
        from api.middleware.auth import (
            generate_api_key, hash_api_key,
            create_signature, verify_signature
        )

        # Generate key
        key = generate_api_key("sk")
        assert key.startswith("sk_"), "Key should start with prefix"
        assert len(key) > 20, "Key should be long enough"

        # Hash key
        hashed = hash_api_key(key)
        assert len(hashed) == 64, "SHA256 hash should be 64 chars"

        # Signature
        payload = '{"test": "data"}'
        secret = "webhook_secret"
        sig = create_signature(payload, secret)

        assert verify_signature(payload, sig, secret), "Signature should verify"
        assert not verify_signature(payload, "wrong", secret), "Wrong sig should fail"

        print(f"  ✓ Key generation: {key[:20]}...")
        print(f"  ✓ Key hashing: {hashed[:20]}...")
        print(f"  ✓ Signature creation: OK")
        print(f"  ✓ Signature verification: OK")
        return True
    except Exception as e:
        print(f"  ✗ Auth middleware test failed: {e}")
        return False


def test_rate_limiter():
    """Test rate limiting."""
    print("\n[2/4] Testing Rate Limiter...")
    try:
        from api.middleware.rate_limit import SlidingWindowLimiter, TokenBucket

        # Sliding window
        limiter = SlidingWindowLimiter(limit=5, window_seconds=60)

        results = []
        for i in range(7):
            allowed, retry = limiter.is_allowed("test")
            results.append(allowed)

        allowed_count = sum(results)
        assert allowed_count == 5, f"Should allow exactly 5, got {allowed_count}"

        # Token bucket
        bucket = TokenBucket(rate=10, capacity=10)

        # Consume all tokens
        for _ in range(10):
            bucket.consume()

        # Should be rate limited now
        assert not bucket.consume(), "Should be rate limited"

        print(f"  ✓ Sliding window: {allowed_count}/5 allowed")
        print(f"  ✓ Token bucket: rate limiting works")
        return True
    except Exception as e:
        print(f"  ✗ Rate limiter test failed: {e}")
        return False


def test_schemas():
    """Test API schemas."""
    print("\n[3/4] Testing API Schemas...")
    try:
        from api.schemas.request import OCRRequest, WebhookRequest
        from api.schemas.response import HealthResponse, OCRResponse

        # OCR Request
        req = OCRRequest(max_tokens=2048, output_format="json")
        assert req.max_tokens == 2048, "Max tokens mismatch"
        assert req.output_format == "json", "Format mismatch"

        # Webhook Request
        wh = WebhookRequest(url="https://example.com/webhook")
        assert wh.url == "https://example.com/webhook", "URL mismatch"

        # Health Response
        health = HealthResponse(
            status="healthy",
            model_loaded=True,
            gpu_available=False,
            version="1.0.0",
            timestamp="2024-01-01T00:00:00"
        )
        assert health.status == "healthy", "Status mismatch"

        print(f"  ✓ OCRRequest schema: OK")
        print(f"  ✓ WebhookRequest schema: OK")
        print(f"  ✓ HealthResponse schema: OK")
        return True
    except Exception as e:
        print(f"  ✗ Schemas test failed: {e}")
        return False


def test_webhook_manager():
    """Test webhook manager."""
    print("\n[4/4] Testing Webhook Manager...")
    try:
        from api.routes.webhook import WebhookManager

        manager = WebhookManager()

        # Register
        webhook_id = manager.register(
            url="https://example.com/webhook",
            events=["document.processed"]
        )
        assert webhook_id, "Should return webhook ID"

        # Get webhook
        webhook = manager.get_webhook(webhook_id)
        assert webhook["url"] == "https://example.com/webhook", "URL mismatch"
        assert "document.processed" in webhook["events"], "Event missing"

        # List webhooks
        webhooks = manager.list_webhooks()
        assert len(webhooks) >= 1, "Should have at least 1 webhook"

        # Get by event
        event_hooks = manager.get_webhooks_for_event("document.processed")
        assert len(event_hooks) >= 1, "Should find webhook for event"

        # Unregister
        result = manager.unregister(webhook_id)
        assert result, "Should unregister successfully"

        print(f"  ✓ Register webhook: {webhook_id[:8]}...")
        print(f"  ✓ Get webhook: OK")
        print(f"  ✓ List webhooks: {len(webhooks)} found")
        print(f"  ✓ Unregister: OK")
        return True
    except Exception as e:
        print(f"  ✗ Webhook manager test failed: {e}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("NANONETS VL - API TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time.time()

    tests = [
        test_auth_middleware,
        test_rate_limiter,
        test_schemas,
        test_webhook_manager,
    ]

    results = []
    for test in tests:
        results.append(test())

    elapsed = time.time() - start_time
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    print(f"  Time: {elapsed:.2f}s")
    print("=" * 60)

    if passed == total:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
