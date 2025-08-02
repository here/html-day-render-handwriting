import simplejson as json
import requests
import os
from typing import Dict, Any

def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified Digital Ocean Functions entry point using requests
    """
    try:
        # Get request parameters
        method = args.get("method", "GET")
        path = args.get("path", "")
        headers = args.get("headers", {})
        body = args.get("body", "")
        api_type = args.get("api_type", "anthropic")
        
        # Handle health check
        if path == "health" or path == "/health":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "Proxy server is running", 
                    "version": "1.0.0",
                    "message": "Function is working correctly"
                })
            }
        
        # Handle test endpoints
        if path == "test-anthropic" or path == "/test-anthropic":
            return handle_test_anthropic(headers)
        
        if path == "test-openai" or path == "/test-openai":
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
                "body": json.dumps({
                    "error": "Invalid api_type. Use 'anthropic' or 'openai'",
                    "received": api_type
                })
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": f"Function error: {str(e)}",
                "type": "exception"
            })
        }

def handle_anthropic_proxy(method: str, path: str, headers: Dict, body: str) -> Dict[str, Any]:
    """Handle Anthropic API proxy requests"""
    try:
        # Parse request data
        request_data = json.loads(body) if body else {}
        
        # Prepare target URL
        target_url = f"https://api.anthropic.com/v1/{path}"
        
        # Prepare headers
        proxy_headers = {
            "x-api-key": headers.get("x-api-key"),
            "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
            "content-type": "application/json"
        }
        
        # Remove None values
        proxy_headers = {k: v for k, v in proxy_headers.items() if v is not None}
        
        # Make request
        response = requests.post(
            target_url,
            json=request_data,
            headers=proxy_headers,
            timeout=30.0
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
            "body": json.dumps({
                "error": f"Anthropic proxy error: {str(e)}",
                "type": "anthropic_error"
            })
        }

def handle_openai_proxy(method: str, path: str, headers: Dict, body: str) -> Dict[str, Any]:
    """Handle OpenAI API proxy requests"""
    try:
        # Parse request data
        request_data = json.loads(body) if body else {}
        
        # Prepare target URL
        target_url = f"https://api.openai.com/v1/{path}"
        
        # Get API key from headers or environment variable
        api_key = headers.get("authorization")
        if not api_key:
            # Try to get from environment variable
            env_api_key = os.environ.get("openai_api_key")
            if env_api_key:
                api_key = f"Bearer {env_api_key}"
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "No OpenAI API key provided in headers or environment variable 'openai_api_key'",
                        "type": "missing_key"
                    })
                }
        
        # Prepare headers
        proxy_headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        # Make request
        response = requests.post(
            target_url,
            json=request_data,
            headers=proxy_headers,
            timeout=30.0
        )
        
        # Debug logging
        print(f"OpenAI response status: {response.status_code}")
        print(f"OpenAI response text: {response.text[:200]}...")
        
        return {
            "statusCode": response.status_code,
            "headers": {"Content-Type": "application/json"},
            "body": response.text if response.text else "{}"
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": f"OpenAI proxy error: {str(e)}",
                "type": "openai_error"
            })
        }

def handle_test_anthropic(headers: Dict) -> Dict[str, Any]:
    """Handle Anthropic API test requests"""
    try:
        api_key = headers.get("x-api-key")
        
        if not api_key:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "No API key provided",
                    "type": "missing_key"
                })
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
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            json=test_data,
            headers=proxy_headers,
            timeout=30.0
        )
        
        response_text = response.text
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": response.status_code,
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "type": "test_success"
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e),
                "type": "test_error"
            })
        }

def handle_test_openai(headers: Dict) -> Dict[str, Any]:
    """Handle OpenAI API test requests"""
    try:
        # Get API key from headers or environment variable
        api_key = headers.get("authorization")
        if not api_key:
            # Try to get from environment variable
            env_api_key = os.environ.get("openai_api_key")
            if env_api_key:
                api_key = f"Bearer {env_api_key}"
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "No OpenAI API key provided in headers or environment variable 'openai_api_key'",
                        "type": "missing_key"
                    })
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
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=test_data,
            headers=proxy_headers,
            timeout=30.0
        )
        
        response_text = response.text
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": response.status_code,
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "type": "test_success"
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e),
                "type": "test_error"
            })
        } 