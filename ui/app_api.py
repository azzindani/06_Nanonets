"""
Gradio web interface for document OCR processing via API backend.

This app communicates with the FastAPI backend via HTTP calls instead of 
directly importing core modules.
"""
import warnings
# Suppress known compatibility warnings
warnings.filterwarnings("ignore", message=".*MessageFactory.*")
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import gradio as gr
import json
import os
from datetime import datetime

from ui.api_client import get_api_client, OCRAPIClient



def get_sample_documents():
    """Get sample document paths from tests/asset directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    asset_dir = os.path.join(base_dir, "tests", "asset")

    samples = []
    sample_names = []

    if os.path.exists(asset_dir):
        sample_files = [
            ("invoice1.pdf", "Invoice PDF"),
            ("docparsing_example1.jpg", "Document 1"),
            ("docparsing_example2.jpg", "Document 2"),
            ("ocr_example1.jpg", "OCR Example 1"),
            ("ocr_example2.jpg", "OCR Example 2"),
            ("docparsing_example3.jpg", "Document 3"),
        ]

        for filename, name in sample_files:
            filepath = os.path.join(asset_dir, filename)
            if os.path.exists(filepath):
                samples.append(filepath)
                sample_names.append(name)

    return samples, sample_names


def check_api_connection(api_url: str, api_key: str):
    """Check connection to API server."""
    try:
        client = get_api_client(base_url=api_url, api_key=api_key)
        result = client.health_check()
        
        if result.success:
            data = result.data
            status = f"✅ Connected\n"
            status += f"Status: {data.get('status', 'unknown')}\n"
            status += f"Model Loaded: {data.get('model_loaded', False)}\n"
            status += f"GPU Available: {data.get('gpu_available', False)}\n"
            status += f"Version: {data.get('version', 'unknown')}"
            return status
        else:
            return f"❌ Connection Failed\n{result.error}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_model_info(api_url: str, api_key: str):
    """Get model information from API."""
    try:
        client = get_api_client(base_url=api_url, api_key=api_key)
        result = client.get_model_info()
        
        if result.success:
            data = result.data
            info = f"Model: {data.get('name', 'unknown')}\n"
            info += f"Device: {data.get('device', 'unknown')}\n"
            info += f"Quantization: {data.get('quantization', 'none')}\n"
            info += f"Memory Used: {data.get('memory_used_gb', 0):.2f} GB\n"
            info += f"Loaded: {data.get('is_loaded', False)}"
            return info
        else:
            return f"Error: {result.error}"
    except Exception as e:
        return f"Error: {str(e)}"


def process_document_via_api(
    file, 
    api_url: str,
    api_key: str,
    max_tokens: int,
    max_image_size: int,
    output_format: str,
    confidence_threshold: float,
    use_v2_api: bool
):
    """Process document through the API backend."""
    
    if file is None:
        return (
            "Error: No file provided.",  # status
            "",   # ocr_text
            "",   # api_response
            "",   # extracted_fields
            "",   # structured_output
            "",   # tables_html
            "",   # entities
            ""    # document_info
        )
    
    try:
        client = get_api_client(base_url=api_url, api_key=api_key)
        
        # Check API connection first
        health = client.health_check()
        if not health.success:
            return (
                f"❌ API Connection Failed: {health.error}",
                "", "", "", "", "", "", ""
            )
        
        # Process document
        if use_v2_api:
            result = client.process_document_v2(
                file_path=file.name,
                max_tokens=max_tokens
            )
        else:
            result = client.process_document(
                file_path=file.name,
                max_tokens=max_tokens,
                max_image_size=max_image_size,
                output_format=output_format,
                extract_fields=True,
                structured_output=True,
                detect_language=True,
                classify_document=True,
                confidence_threshold=confidence_threshold
            )
        
        if not result.success:
            return (
                f"❌ Processing Failed: {result.error}",
                "", "", "", "", "", "", ""
            )
        
        data = result.data
        
        # Format status
        if use_v2_api:
            processing_time = data.get("processing_time_ms", 0)
            doc_info = data.get("document", {})
            status = f"""✅ Processing Complete (API v2)

Job ID: {data.get('job_id', 'N/A')}
Processing Time: {processing_time} ms
Status: {data.get('status', 'N/A')}

Document Info:
- Filename: {doc_info.get('filename', 'N/A')}
- Size: {doc_info.get('file_size_mb', 0):.3f} MB
- Type: {doc_info.get('file_type', 'N/A')}
- Pages: {doc_info.get('total_pages', 0)}"""

            result_data = data.get("result", {})
            ocr_text = result_data.get("raw_text", "")
            
            # Structured output
            structured_output = json.dumps(result_data, indent=2)
            
            # Extracted fields
            extracted_fields = json.dumps(
                result_data.get("extracted_fields", {}), 
                indent=2
            )
            
            # Entities
            entities = json.dumps(
                result_data.get("entities", []), 
                indent=2
            )
            
            # Tables
            tables_html = ""
            line_items = result_data.get("line_items", [])
            if line_items:
                tables_html = "<table border='1' style='border-collapse: collapse;'>"
                tables_html += "<tr><th>Description</th><th>Quantity</th><th>Price</th><th>Total</th></tr>"
                for item in line_items:
                    tables_html += f"<tr><td>{item.get('description', '')}</td>"
                    tables_html += f"<td>{item.get('quantity', '')}</td>"
                    tables_html += f"<td>{item.get('unit_price', '')}</td>"
                    tables_html += f"<td>{item.get('total', '')}</td></tr>"
                tables_html += "</table>"
            
            # Document info
            document_info = f"""Document Type: {result_data.get('document_type', 'N/A')}
Language: {result_data.get('language', 'N/A')}
Confidence: {result_data.get('confidence', 0):.2f}
Total Entities: {len(result_data.get('entities', []))}
Line Items: {len(line_items)}"""

        else:
            # API v1 response
            processing_time = data.get("processing_time_ms", 0)
            doc_meta = data.get("document", {})
            result_data = data.get("result", {})
            
            status = f"""✅ Processing Complete (API v1)

Job ID: {data.get('job_id', 'N/A')}
Processing Time: {processing_time} ms
Status: {data.get('status', 'N/A')}

Document Info:
- Filename: {doc_meta.get('filename', 'N/A')}
- Size: {doc_meta.get('file_size_mb', 0):.3f} MB
- Type: {doc_meta.get('file_type', 'N/A')}
- Pages: {doc_meta.get('total_pages', 0)}

Content Detection:
- Tables: {result_data.get('tables_count', 0)}
- Equations: {result_data.get('equations_count', 0)}"""

            ocr_text = result_data.get("text", "")
            
            # Extracted fields
            extracted_fields = json.dumps(
                data.get("extracted_fields", {}), 
                indent=2
            )
            
            # Structured output
            structured = result_data.get("structured", {})
            structured_output = json.dumps(structured, indent=2)
            
            # Entities from structured
            entities = json.dumps(
                structured.get("entities", []) if structured else [], 
                indent=2
            )
            
            # Tables - formatted output
            tables_html = result_data.get("formatted_output", "")
            if output_format == "json":
                try:
                    parsed = json.loads(tables_html)
                    tables_html = json.dumps(parsed, indent=2)
                except:
                    pass
            
            # Document info
            document_info = f"""Document Type: {result_data.get('document_type', 'N/A')}
Classification Confidence: {result_data.get('classification_confidence', 'N/A')}
Language: {result_data.get('language', 'N/A')}

Confidence Scores:
{json.dumps(data.get('confidence_scores', {}), indent=2)}"""

        # Full API response
        api_response = json.dumps(data, indent=2)
        
        return (
            status,
            ocr_text,
            api_response,
            extracted_fields,
            structured_output,
            tables_html,
            entities,
            document_info
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return (
            f"❌ Error: {str(e)}\n\n{error_trace}",
            "", "", "", "", "", "", ""
        )


def create_gradio_interface(default_api_url: str = "http://localhost:8000"):
    """Create and return the Gradio interface."""
    
    sample_images, sample_names = get_sample_documents()
    
    custom_css = """
    .status-box {
        font-family: monospace;
        white-space: pre-wrap;
    }
    .small-upload span,
    .small-upload .upload-button,
    .small-upload button {
        font-size: 9px !important;
    }
    """
    
    with gr.Blocks(theme=gr.themes.Default(), css=custom_css) as demo:
        gr.Markdown("""
        # 🔌 Nanonets-OCR API Client
        
        **Document OCR Processing via API Backend** | Connects to FastAPI server
        """)
        
        with gr.Tabs():
            # Tab 1: Connection & Process
            with gr.TabItem("📡 Process Document"):
                with gr.Row():
                    # Left column: Connection & Upload
                    with gr.Column(scale=1):
                        gr.Markdown("### API Connection")
                        api_url = gr.Textbox(
                            label="API URL",
                            value=default_api_url,
                            info="FastAPI server URL"
                        )
                        api_key = gr.Textbox(
                            label="API Key (optional)",
                            type="password",
                            value="",
                            info="Leave empty if not required"
                        )
                        
                        with gr.Row():
                            check_btn = gr.Button("🔍 Check Connection", size="sm")
                            model_btn = gr.Button("ℹ️ Model Info", size="sm")
                        
                        connection_status = gr.Textbox(
                            label="Connection Status",
                            lines=6,
                            interactive=False,
                            elem_classes=["status-box"]
                        )
                        
                        gr.Markdown("### Upload Document")
                        file_input = gr.File(
                            label="Upload Document",
                            file_types=["image", ".pdf"],
                            interactive=True,
                            height=100,
                            elem_classes=["small-upload"]
                        )
                        
                        process_button = gr.Button(
                            "🚀 Process Document", 
                            variant="primary", 
                            size="lg"
                        )
                    
                    # Right column: Settings
                    with gr.Column(scale=1):
                        gr.Markdown("### Processing Settings")
                        
                        use_v2_api = gr.Checkbox(
                            label="Use API v2 (Enhanced Structured Output)",
                            value=True,
                            info="V2 provides cleaner structured format"
                        )
                        
                        max_tokens = gr.Slider(
                            minimum=500, maximum=6000, step=250, value=2048,
                            label="Max Tokens",
                            info="Maximum tokens for OCR output"
                        )
                        
                        max_image_size = gr.Slider(
                            minimum=512, maximum=2048, step=128, value=1536,
                            label="Max Image Size (px)",
                            info="Resize images to this max dimension"
                        )
                        
                        output_format = gr.Dropdown(
                            choices=["json", "xml", "csv"],
                            value="json",
                            label="Output Format (v1 only)"
                        )
                        
                        confidence_threshold = gr.Slider(
                            minimum=0.0, maximum=1.0, step=0.05, value=0.75,
                            label="Confidence Threshold",
                            info="Minimum confidence for field extraction"
                        )
                        
                        # Status display
                        gr.Markdown("### Processing Status")
                        status_output = gr.Textbox(
                            label="Status",
                            lines=12,
                            interactive=False,
                            elem_classes=["status-box"]
                        )
                
                # Sample documents
                if sample_images:
                    gr.Markdown("**Sample Documents** - Click to load:")
                    gr.Examples(
                        examples=[[path] for path in sample_images],
                        inputs=[file_input],
                        examples_per_page=6,
                        label="Sample Documents"
                    )
            
            # Tab 2: Results
            with gr.TabItem("📄 Results"):
                with gr.Tabs():
                    with gr.TabItem("Full OCR Text"):
                        ocr_text_output = gr.Textbox(
                            label="Extracted Text",
                            lines=25,
                            show_copy_button=True
                        )
                    
                    with gr.TabItem("API Response"):
                        api_response_output = gr.Code(
                            label="Raw API Response",
                            language="json",
                            lines=25
                        )
                    
                    with gr.TabItem("Extracted Fields"):
                        extracted_fields_output = gr.Code(
                            label="Extracted Fields",
                            language="json",
                            lines=25
                        )
                    
                    with gr.TabItem("Structured Output"):
                        structured_output_display = gr.Code(
                            label="Structured Output",
                            language="json",
                            lines=25
                        )
                    
                    with gr.TabItem("Tables / Formatted"):
                        tables_output = gr.HTML(
                            label="Tables & Formatted Content"
                        )
                    
                    with gr.TabItem("Entities"):
                        entities_output = gr.Code(
                            label="Extracted Entities",
                            language="json",
                            lines=25
                        )
                    
                    with gr.TabItem("Document Info"):
                        document_info_output = gr.Textbox(
                            label="Document Information",
                            lines=15
                        )
            
            # Tab 3: Help
            with gr.TabItem("❓ Help"):
                gr.Markdown("""
                ## How to Use
                
                ### 1. Start the API Server
                Before using this UI, make sure the API server is running:
                
                ```bash
                python -m api.server
                ```
                
                The server should start at `http://localhost:8000` by default.
                
                ### 2. Check Connection
                1. Enter the API URL (default: `http://localhost:8000`)
                2. Enter API key if required
                3. Click "Check Connection" to verify
                
                ### 3. Process Documents
                1. Upload a document (PDF or image)
                2. Adjust processing settings if needed
                3. Click "Process Document"
                4. View results in the Results tab
                
                ### API Endpoints Used
                
                | Endpoint | Description |
                |----------|-------------|
                | `GET /api/v1/health` | Health check |
                | `GET /api/v1/models` | Model information |
                | `POST /api/v1/ocr` | Process document (v1) |
                | `POST /api/v1/v2/ocr` | Process document (v2) |
                
                ### API v1 vs v2
                
                - **v1**: More options, legacy format, includes raw formatted output
                - **v2**: Cleaner structured format, optimized for downstream processing
                
                ### Troubleshooting
                
                - **Connection Failed**: Make sure API server is running
                - **Timeout**: Large documents may take longer, increase timeout
                - **Auth Error**: Check API key if authentication is enabled
                """)
        
        # Event handlers
        check_btn.click(
            fn=check_api_connection,
            inputs=[api_url, api_key],
            outputs=[connection_status]
        )
        
        model_btn.click(
            fn=get_model_info,
            inputs=[api_url, api_key],
            outputs=[connection_status]
        )
        
        process_button.click(
            fn=process_document_via_api,
            inputs=[
                file_input,
                api_url,
                api_key,
                max_tokens,
                max_image_size,
                output_format,
                confidence_threshold,
                use_v2_api
            ],
            outputs=[
                status_output,
                ocr_text_output,
                api_response_output,
                extracted_fields_output,
                structured_output_display,
                tables_output,
                entities_output,
                document_info_output
            ]
        )
    
    return demo


def run_api_ui(
    api_url: str = "http://localhost:8000",
    server_name: str = "0.0.0.0",
    server_port: int = 7861,
    share: bool = False
):
    """
    Run the API-based Gradio interface.
    
    Args:
        api_url: Default API server URL
        server_name: Gradio server name
        server_port: Gradio server port
        share: Whether to create a public link
    """
    print("=" * 60)
    print("GRADIO API CLIENT UI")
    print("=" * 60)
    print(f"  API URL: {api_url}")
    print(f"  UI URL: http://{server_name}:{server_port}")
    print("=" * 60)
    
    # Check API connection on startup
    client = get_api_client(base_url=api_url)
    health = client.health_check()
    if health.success:
        print("  ✓ API server is accessible")
    else:
        print(f"  ⚠ API server not responding: {health.error}")
        print("  Make sure to start the API server: python -m api.server")
    print("=" * 60)
    
    demo = create_gradio_interface(default_api_url=api_url)
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=share
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run OCR API Client UI")
    parser.add_argument(
        "--api-url", 
        default="http://localhost:8000",
        help="API server URL"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=7861,
        help="UI server port"
    )
    parser.add_argument(
        "--share", 
        action="store_true",
        help="Create public link"
    )
    
    args = parser.parse_args()
    
    run_api_ui(
        api_url=args.api_url,
        server_port=args.port,
        share=args.share
    )
