"""
Test all services (cache, queue, storage).

Run with: python -m services.test_services
"""
import sys
import time
import tempfile
from datetime import datetime


def test_cache_service():
    """Test cache service."""
    print("\n[1/3] Testing Cache Service...")
    try:
        from services.cache import CacheService

        cache = CacheService()

        # Set/Get
        cache.set("test_key", {"data": "value", "number": 42})
        result = cache.get("test_key")
        assert result["data"] == "value", "Data mismatch"
        assert result["number"] == 42, "Number mismatch"

        # Exists
        assert cache.exists("test_key"), "Key should exist"
        assert not cache.exists("nonexistent"), "Key should not exist"

        # Delete
        cache.delete("test_key")
        assert not cache.exists("test_key"), "Key should be deleted"

        # OCR result caching
        file_content = b"test document content"
        params = {"max_tokens": 2048}
        ocr_result = {"text": "extracted text", "pages": 1}

        key = cache.cache_ocr_result(file_content, params, ocr_result)
        assert key.startswith("ocr:"), "Key should start with ocr:"

        cached = cache.get_ocr_result(file_content, params)
        assert cached == ocr_result, "Cached result mismatch"

        # Stats
        stats = cache.get_stats()
        assert "type" in stats, "Stats should have type"

        print(f"  ✓ Set/Get: OK")
        print(f"  ✓ Exists check: OK")
        print(f"  ✓ Delete: OK")
        print(f"  ✓ OCR result caching: OK")
        print(f"  ✓ Stats: {stats['type']}")
        return True
    except Exception as e:
        print(f"  ✗ Cache service test failed: {e}")
        return False


def test_queue_service():
    """Test job queue service."""
    print("\n[2/3] Testing Queue Service...")
    try:
        from services.queue import JobQueue, JobPriority

        queue = JobQueue()

        # Enqueue jobs
        job1 = queue.enqueue("ocr", {"file": "doc1.pdf"}, JobPriority.NORMAL)
        job2 = queue.enqueue("ocr", {"file": "doc2.pdf"}, JobPriority.HIGH)

        assert job1, "Should return job ID"
        assert job2, "Should return job ID"

        # Get status
        status = queue.get_job_status(job1)
        assert status["status"] == "pending", "Job should be pending"
        assert status["task_type"] == "ocr", "Task type mismatch"

        # Dequeue (high priority first)
        job = queue.dequeue(timeout=1)
        assert job.id == job2, "High priority job should come first"

        # Complete job
        queue.complete_job(job2, {"text": "extracted"})
        status = queue.get_job_status(job2)
        assert status["status"] == "completed", "Job should be completed"
        assert status["result"]["text"] == "extracted", "Result mismatch"

        # Fail job
        job = queue.dequeue(timeout=1)
        queue.fail_job(job1, "Test error")
        status = queue.get_job_status(job1)
        assert status["retries"] == 1, "Should have 1 retry"

        # Stats
        stats = queue.get_queue_stats()
        assert "total_jobs" in stats, "Stats should have total_jobs"

        print(f"  ✓ Enqueue: {job1[:8]}..., {job2[:8]}...")
        print(f"  ✓ Priority ordering: OK")
        print(f"  ✓ Complete job: OK")
        print(f"  ✓ Fail/retry: OK")
        print(f"  ✓ Stats: {stats['total_jobs']} jobs")
        return True
    except Exception as e:
        print(f"  ✗ Queue service test failed: {e}")
        return False


def test_storage_service():
    """Test storage service."""
    print("\n[3/3] Testing Storage Service...")
    try:
        from services.storage import StorageService

        with tempfile.TemporaryDirectory() as tmp:
            storage = StorageService(tmp)

            # Save upload
            content = b"Test document content for storage"
            stored = storage.save_upload("test_doc.pdf", content, "application/pdf")

            assert stored.file_id, "Should have file ID"
            assert stored.filename == "test_doc.pdf", "Filename mismatch"
            assert stored.size_bytes == len(content), "Size mismatch"

            # Get upload
            retrieved = storage.get_upload(stored.file_id)
            assert retrieved == content, "Content mismatch"

            # Save result
            job_id = "test-job-123"
            result = {"text": "processed content", "pages": 1}
            result_path = storage.save_result(job_id, result)
            assert result_path, "Should return path"

            # Get result
            loaded = storage.get_result(job_id)
            assert loaded == result, "Result mismatch"

            # Temp file
            temp_path = storage.create_temp_file(".pdf")
            assert temp_path.endswith(".pdf"), "Should have extension"

            # Stats
            stats = storage.get_storage_stats()
            assert "uploads" in stats, "Stats should have uploads"
            assert stats["uploads"]["files"] == 1, "Should have 1 upload"

            # Cleanup
            storage.delete_upload(stored.file_id)
            storage.delete_result(job_id)

            print(f"  ✓ Save upload: {stored.file_id}")
            print(f"  ✓ Get upload: {len(retrieved)} bytes")
            print(f"  ✓ Save result: OK")
            print(f"  ✓ Get result: OK")
            print(f"  ✓ Temp files: OK")
            print(f"  ✓ Cleanup: OK")

        return True
    except Exception as e:
        print(f"  ✗ Storage service test failed: {e}")
        return False


def main():
    """Run all service tests."""
    print("=" * 60)
    print("NANONETS VL - SERVICES TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time.time()

    tests = [
        test_cache_service,
        test_queue_service,
        test_storage_service,
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
