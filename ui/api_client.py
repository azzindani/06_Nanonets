"""
API Client for communicating with the FastAPI OCR backend.
"""
import os
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: int = 0


class OCRAPIClient:
    """HTTP client for the Nanonets OCR API backend."""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 300
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server (default: http://localhost:8000)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 300 for large documents)
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.timeout = timeout
        self.api_prefix = "/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        files: Dict = None,
        data: Dict = None,
        params: Dict = None
    ) -> APIResponse:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                files=files,
                data=data,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return APIResponse(
                    success=True,
                    data=response.json(),
                    status_code=response.status_code
                )
            else:
                error_detail = response.json().get("detail", response.text)
                return APIResponse(
                    success=False,
                    error=f"API Error ({response.status_code}): {error_detail}",
                    status_code=response.status_code
                )
                
        except requests.exceptions.ConnectionError:
            return APIResponse(
                success=False,
                error=f"Connection failed. Is the API server running at {self.base_url}?"
            )
        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                error=f"Request timed out after {self.timeout} seconds"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Request failed: {str(e)}"
            )
    
    def health_check(self) -> APIResponse:
        """Check if the API server is healthy."""
        return self._make_request("GET", "/health")
    
    def get_model_info(self) -> APIResponse:
        """Get information about the loaded model."""
        return self._make_request("GET", "/models")
    
    def get_status(self) -> APIResponse:
        """Get detailed server status including model loading state."""
        # Note: /status is at root level, not under api_prefix
        url = f"{self.base_url}/status"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            if response.status_code == 200:
                return APIResponse(success=True, data=response.json(), status_code=200)
            else:
                return APIResponse(success=False, error=response.text, status_code=response.status_code)
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    
    def process_document(
        self,
        file_path: str,
        max_tokens: int = 2048,
        max_image_size: int = 1536,
        output_format: str = "json",
        extract_fields: bool = True,
        structured_output: bool = True,
        detect_language: bool = True,
        classify_document: bool = True,
        webhook_url: str = None,
        confidence_threshold: float = 0.75
    ) -> APIResponse:
        """
        Process a document with OCR (API v1).
        
        Args:
            file_path: Path to the document file
            max_tokens: Maximum tokens for generation
            max_image_size: Maximum image dimension
            output_format: Output format (json, xml, csv)
            extract_fields: Whether to extract predefined fields
            structured_output: Whether to return enhanced structured output
            detect_language: Whether to detect document language
            classify_document: Whether to classify document type
            webhook_url: URL for webhook callback
            confidence_threshold: Minimum confidence for field extraction
            
        Returns:
            APIResponse with OCR results
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {
                "max_tokens": max_tokens,
                "max_image_size": max_image_size,
                "output_format": output_format,
                "extract_fields": extract_fields,
                "structured_output": structured_output,
                "detect_language": detect_language,
                "classify_document": classify_document,
                "confidence_threshold": confidence_threshold
            }
            if webhook_url:
                data["webhook_url"] = webhook_url
                
            return self._make_request("POST", "/ocr", files=files, data=data)
    
    def process_document_v2(
        self,
        file_path: str,
        max_tokens: int = 2048,
        webhook_url: str = None
    ) -> APIResponse:
        """
        Process a document with OCR (API v2 - enhanced structured output).
        
        Args:
            file_path: Path to the document file
            max_tokens: Maximum tokens for generation
            webhook_url: Optional webhook URL for callback
            
        Returns:
            APIResponse with structured OCR results
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"max_tokens": max_tokens}
            if webhook_url:
                data["webhook_url"] = webhook_url
                
            return self._make_request("POST", "/v2/ocr", files=files, data=data)
    
    def classify_document(self, file_path: str) -> APIResponse:
        """
        Classify document type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            APIResponse with classification results
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            return self._make_request("POST", "/classify", files=files)
    
    def detect_language(self, file_path: str) -> APIResponse:
        """
        Detect document language.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            APIResponse with language detection results
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            return self._make_request("POST", "/detect-language", files=files)
    
    def extract_entities(self, file_path: str) -> APIResponse:
        """
        Extract entities from document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            APIResponse with extracted entities
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            return self._make_request("POST", "/extract-entities", files=files)
    
    def get_structured_output(
        self,
        file_path: str,
        max_tokens: int = 2048
    ) -> APIResponse:
        """
        Get fully structured output from document.
        
        Args:
            file_path: Path to the document file
            max_tokens: Maximum tokens for generation
            
        Returns:
            APIResponse with structured output
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"max_tokens": max_tokens}
            return self._make_request("POST", "/structured", files=files, data=data)
    
    def process_batch(
        self,
        file_paths: List[str],
        max_tokens: int = 2048
    ) -> APIResponse:
        """
        Process multiple documents in batch.
        
        Args:
            file_paths: List of paths to document files
            max_tokens: Maximum tokens for generation per document
            
        Returns:
            APIResponse with batch processing results
        """
        files = []
        file_handles = []
        
        try:
            for path in file_paths:
                f = open(path, "rb")
                file_handles.append(f)
                files.append(("files", (os.path.basename(path), f)))
            
            data = {"max_tokens": max_tokens}
            return self._make_request("POST", "/ocr/batch", files=files, data=data)
        finally:
            for f in file_handles:
                f.close()


# Global client instance
_api_client: Optional[OCRAPIClient] = None


def get_api_client(base_url: str = None, api_key: str = None) -> OCRAPIClient:
    """
    Get or create the global API client instance.
    
    Args:
        base_url: Base URL of the API server
        api_key: Optional API key
        
    Returns:
        OCRAPIClient instance
    """
    global _api_client
    
    if _api_client is None or base_url is not None:
        _api_client = OCRAPIClient(base_url=base_url, api_key=api_key)
    
    return _api_client


if __name__ == "__main__":
    print("=" * 60)
    print("API CLIENT MODULE TEST")
    print("=" * 60)
    
    client = OCRAPIClient()
    print(f"  Base URL: {client.base_url}")
    print(f"  API Prefix: {client.api_prefix}")
    
    # Test health check
    result = client.health_check()
    if result.success:
        print(f"  ✓ API is healthy: {result.data}")
    else:
        print(f"  ✗ API check failed: {result.error}")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
