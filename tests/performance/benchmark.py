#!/usr/bin/env python3
"""
Benchmark script for measuring OCR processing performance.

Usage:
    python tests/performance/benchmark.py
    python tests/performance/benchmark.py --iterations 100 --image-size 1024
"""
import argparse
import time
import statistics
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from PIL import Image
import io

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class Benchmark:
    """Performance benchmark for OCR system."""

    def __init__(self, iterations: int = 10, image_size: int = 512):
        """
        Initialize benchmark.

        Args:
            iterations: Number of iterations per test.
            image_size: Size of test images (width=height).
        """
        self.iterations = iterations
        self.image_size = image_size
        self.results: Dict[str, List[float]] = {}

    def create_test_image(self, size: int = None) -> Image.Image:
        """Create a test image with some text-like patterns."""
        size = size or self.image_size
        img = Image.new('RGB', (size, size), color='white')

        # Add some patterns to make it more realistic
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)

        # Draw grid lines (simulating text)
        for i in range(0, size, 20):
            draw.line([(0, i), (size, i)], fill='lightgray', width=1)
            # Simulated text blocks
            if i % 40 == 0:
                draw.rectangle([10, i, size - 10, i + 15], fill='black')

        return img

    def benchmark_image_loading(self) -> Dict[str, Any]:
        """Benchmark image loading and preprocessing."""
        from core.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        times = []

        # Create test image
        img = self.create_test_image()
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')

        for _ in range(self.iterations):
            img_bytes.seek(0)

            start = time.perf_counter()
            # Load and preprocess
            loaded_img = Image.open(img_bytes)
            processed = processor.preprocess_image(loaded_img, self.image_size)
            end = time.perf_counter()

            times.append((end - start) * 1000)  # Convert to ms

        return self._calculate_stats("image_loading", times)

    def benchmark_output_parsing(self) -> Dict[str, Any]:
        """Benchmark output parsing."""
        from core.output_parser import OutputParser

        parser = OutputParser()
        times = []

        # Sample OCR output
        sample_output = """
        <table>
            <tr><th>Item</th><th>Qty</th><th>Price</th></tr>
            <tr><td>Widget A</td><td>10</td><td>$99.99</td></tr>
            <tr><td>Widget B</td><td>5</td><td>$149.99</td></tr>
        </table>

        Invoice Number: INV-2024-001
        Date: January 15, 2024
        Total: $1,249.90

        $$E = mc^2$$

        <img>Company Logo</img>
        """ * 5  # Multiply to simulate larger document

        for _ in range(self.iterations):
            start = time.perf_counter()
            parsed = parser.parse(sample_output)
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("output_parsing", times)

    def benchmark_field_extraction(self) -> Dict[str, Any]:
        """Benchmark field extraction."""
        from core.field_extractor import FieldExtractor

        extractor = FieldExtractor()
        times = []

        sample_text = """
        INVOICE

        From: Acme Corporation
        123 Business Street
        New York, NY 10001
        Phone: (555) 123-4567
        Email: billing@acme.com

        To: Customer Inc.
        456 Client Avenue
        Los Angeles, CA 90001

        Invoice Number: INV-2024-001
        Invoice Date: January 15, 2024
        Due Date: February 15, 2024
        PO Number: PO-12345

        Items:
        - Widget A (10 x $99.99) = $999.90
        - Widget B (5 x $149.99) = $749.95

        Subtotal: $1,749.85
        Tax (8%): $139.99
        Total Due: $1,889.84

        Payment Terms: Net 30
        """

        predefined_fields = [
            "Invoice Number", "Invoice Date", "Due Date",
            "Subtotal", "Tax", "Total"
        ]

        for _ in range(self.iterations):
            start = time.perf_counter()
            results = extractor.extract(sample_text, predefined_fields, [])
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("field_extraction", times)

    def benchmark_format_conversion(self) -> Dict[str, Any]:
        """Benchmark format conversion."""
        from core.output_parser import OutputParser
        from core.format_converter import FormatConverter

        parser = OutputParser()
        converter = FormatConverter()
        times = []

        sample_output = """
        <table>
            <tr><th>Item</th><th>Price</th></tr>
            <tr><td>A</td><td>$10</td></tr>
        </table>
        Some text content here.
        """

        parsed = parser.parse(sample_output)

        for _ in range(self.iterations):
            start = time.perf_counter()
            json_out = converter.to_json(parsed)
            xml_out = converter.to_xml(parsed)
            csv_out = converter.to_csv(parsed)
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("format_conversion", times)

    def benchmark_document_classification(self) -> Dict[str, Any]:
        """Benchmark document classification."""
        from core.document_classifier import DocumentClassifier

        classifier = DocumentClassifier()
        times = []

        sample_texts = [
            # Invoice
            "Invoice Number: INV-001\nTotal Due: $500.00\nPayment Terms: Net 30",
            # Receipt
            "Receipt #12345\nTransaction ID: TXN-999\nPaid by: Credit Card\nTotal: $45.99",
            # Contract
            "This Agreement is entered into by and between Party A and Party B...",
        ]

        for _ in range(self.iterations):
            start = time.perf_counter()
            for text in sample_texts:
                result = classifier.classify(text)
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("document_classification", times)

    def benchmark_language_detection(self) -> Dict[str, Any]:
        """Benchmark language detection."""
        from core.language_support import LanguageDetector

        detector = LanguageDetector()
        times = []

        sample_texts = [
            "The quick brown fox jumps over the lazy dog.",
            "El rápido zorro marrón salta sobre el perro perezoso.",
            "Le rapide renard brun saute par-dessus le chien paresseux.",
            "Der schnelle braune Fuchs springt über den faulen Hund.",
        ]

        for _ in range(self.iterations):
            start = time.perf_counter()
            for text in sample_texts:
                result = detector.detect(text)
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("language_detection", times)

    def benchmark_semantic_extraction(self) -> Dict[str, Any]:
        """Benchmark semantic extraction."""
        from core.semantic_extractor import SemanticExtractor

        extractor = SemanticExtractor()
        times = []

        sample_text = """
        Acme Corporation
        Invoice #INV-2024-001

        Date: January 15, 2024
        Due: February 15, 2024

        Bill To:
        John Smith
        john@example.com
        +1 (555) 123-4567

        Total Amount: $1,500.00
        Tax: $150.00
        """

        for _ in range(self.iterations):
            start = time.perf_counter()
            result = extractor.extract(sample_text)
            end = time.perf_counter()

            times.append((end - start) * 1000)

        return self._calculate_stats("semantic_extraction", times)

    def _calculate_stats(self, name: str, times: List[float]) -> Dict[str, Any]:
        """Calculate statistics for timing results."""
        self.results[name] = times

        return {
            "name": name,
            "iterations": len(times),
            "min_ms": round(min(times), 3),
            "max_ms": round(max(times), 3),
            "mean_ms": round(statistics.mean(times), 3),
            "median_ms": round(statistics.median(times), 3),
            "stdev_ms": round(statistics.stdev(times), 3) if len(times) > 1 else 0,
            "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
            "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3) if len(times) >= 100 else None,
            "throughput_per_sec": round(1000 / statistics.mean(times), 2)
        }

    def run_all(self) -> Dict[str, Any]:
        """Run all benchmarks."""
        print(f"\n{'='*60}")
        print(f"NANONETS OCR BENCHMARK")
        print(f"{'='*60}")
        print(f"Iterations: {self.iterations}")
        print(f"Image size: {self.image_size}x{self.image_size}")
        print(f"{'='*60}\n")

        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "iterations": self.iterations,
                "image_size": self.image_size
            },
            "benchmarks": []
        }

        benchmarks = [
            ("Image Loading", self.benchmark_image_loading),
            ("Output Parsing", self.benchmark_output_parsing),
            ("Field Extraction", self.benchmark_field_extraction),
            ("Format Conversion", self.benchmark_format_conversion),
            ("Document Classification", self.benchmark_document_classification),
            ("Language Detection", self.benchmark_language_detection),
            ("Semantic Extraction", self.benchmark_semantic_extraction),
        ]

        for name, benchmark_func in benchmarks:
            print(f"Running: {name}...")
            try:
                result = benchmark_func()
                results["benchmarks"].append(result)
                print(f"  Mean: {result['mean_ms']:.2f}ms | "
                      f"P95: {result['p95_ms']:.2f}ms | "
                      f"Throughput: {result['throughput_per_sec']}/sec")
            except Exception as e:
                print(f"  ERROR: {e}")
                results["benchmarks"].append({
                    "name": name.lower().replace(" ", "_"),
                    "error": str(e)
                })

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")

        total_mean = sum(
            r["mean_ms"] for r in results["benchmarks"]
            if "mean_ms" in r
        )
        print(f"Total mean time (all benchmarks): {total_mean:.2f}ms")

        return results

    def save_results(self, filepath: str):
        """Save benchmark results to JSON file."""
        results = self.run_all()

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {filepath}")


def main():
    """Run benchmarks from command line."""
    parser = argparse.ArgumentParser(description="Run OCR performance benchmarks")
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=50,
        help="Number of iterations per benchmark"
    )
    parser.add_argument(
        "--image-size", "-s",
        type=int,
        default=512,
        help="Size of test images"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file for results (JSON)"
    )

    args = parser.parse_args()

    benchmark = Benchmark(
        iterations=args.iterations,
        image_size=args.image_size
    )

    if args.output:
        benchmark.save_results(args.output)
    else:
        results = benchmark.run_all()
        print("\n" + json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
