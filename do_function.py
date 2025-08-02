import json
import httpx
from typing import Dict, Any

# Configuration
ANTHROPIC_API_URL = "https://api.anthropic.com"
OPENAI_API_URL = "https://api.openai.com"

def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Digital Ocean Functions entry point
    
    Expected args:
    - method: HTTP method (GET, POST, etc.)
    - path: Request path
    - headers: Request headers
    - body: Request body (for POST requests)
    - api_type: "anthropic" or "openai"
    """
    
    try:
        method = args.get("method", "GET")
        path = args.get("path", "")
        headers = args.get("headers", {})
        body = args.get("body", "")
        api_type = args.get("api_type", "anthropic")
        
        # Handle health check
        if path == "/health" or path == "health":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "Proxy server is running", "version": "1.0.0"})
            }
        
        # Handle test endpoints
        if path == "/test-anthropic" or path == "test-anthropic":
            return handle_test_anthropic(headers)
        
        if path == "/test-openai" or path == "test-openai":
            return handle_test_openai(headers)
        
        # Handle proxy requests
        if api_type == "anthropic":
            return handle_anthropic_proxy(method, path, headers, body)
        elif api_type == "openai":
            return handle_openai_proxy(method, path, headers, body)
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid api_type. Use 'anthropic' or 'openai'"})
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Function error: {str(e)}"})
        }

def handle_anthropic_proxy(method: str, path: str, headers: Dict, body: str) -> Dict[str, Any]:
    """Handle Anthropic API proxy requests"""
    try:
        # Parse request data
        request_data = json.loads(body) if body else {}
        
        # Prepare target URL
        target_url = f"{ANTHROPIC_API_URL}/v1/{path}"
        
        # Prepare headers
        proxy_headers = {
            "x-api-key": headers.get("x-api-key"),
            "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
            "content-type": "application/json"
        }
        
        # Remove None values
        proxy_headers = {k: v for k, v in proxy_headers.items() if v is not None}
        
        # Make request
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                target_url,
                json=request_data,
                headers=proxy_headers
            )
            
            return {
                "statusCode": response.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": response.text
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Anthropic proxy error: {str(e)}"})
        }

def handle_openai_proxy(method: str, path: str, headers: Dict, body: str) -> Dict[str, Any]:
    """Handle OpenAI API proxy requests"""
    try:
        # Parse request data
        request_data = json.loads(body) if body else {}
        
        # Prepare target URL
        target_url = f"{OPENAI_API_URL}/v1/{path}"
        
        # Prepare headers
        proxy_headers = {
            "Authorization": headers.get("authorization"),
            "Content-Type": "application/json"
        }
        
        # Remove None values
        proxy_headers = {k: v for k, v in proxy_headers.items() if v is not None}
        
        # Make request
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                target_url,
                json=request_data,
                headers=proxy_headers
            )
            
            return {
                "statusCode": response.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": response.text
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"OpenAI proxy error: {str(e)}"})
        }

def handle_test_anthropic(headers: Dict) -> Dict[str, Any]:
    """Handle Anthropic API test requests"""
    try:
        api_key = headers.get("x-api-key")
        
        if not api_key:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No API key provided"})
            }
        
        # Simple test request
        test_data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 10,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        }
        
        proxy_headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{ANTHROPIC_API_URL}/v1/messages",
                json=test_data,
                headers=proxy_headers
            )
            
            response_text = response.text
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": response.status_code,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text
                })
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

def handle_test_openai(headers: Dict) -> Dict[str, Any]:
    """Handle OpenAI API test requests"""
    try:
        api_key = headers.get("authorization")
        
        if not api_key:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No API key provided"})
            }
        
        # Simple test request
        test_data = {
            "model": "gpt-4o",
            "max_tokens": 10,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        }
        
        proxy_headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{OPENAI_API_URL}/v1/chat/completions",
                json=test_data,
                headers=proxy_headers
            )
            
            response_text = response.text
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": response.status_code,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text
                })
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        } 