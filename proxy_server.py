from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
import os
from typing import Optional

app = FastAPI(title="OCR Proxy Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ANTHROPIC_API_URL = "https://api.anthropic.com"
OPENAI_API_URL = "https://api.openai.com"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "Proxy server is running", "version": "1.0.0"}

@app.post("/api/anthropic/{path:path}")
async def proxy_anthropic(path: str, request: Request):
    """Proxy requests to Anthropic API"""
    try:
        # Get the request body
        body = await request.body()
        request_data = json.loads(body) if body else {}
        
        # Get headers
        headers = dict(request.headers)
        
        # Forward to Anthropic API
        target_url = f"{ANTHROPIC_API_URL}/v1/{path}"
        
        # Prepare headers for Anthropic
        proxy_headers = {
            "x-api-key": headers.get("x-api-key"),
            "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
            "content-type": "application/json"
        }
        
        # Remove None values
        proxy_headers = {k: v for k, v in proxy_headers.items() if v is not None}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                target_url,
                json=request_data,
                headers=proxy_headers
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.post("/api/openai/{path:path}")
async def proxy_openai(path: str, request: Request):
    """Proxy requests to OpenAI API"""
    try:
        # Get the request body
        body = await request.body()
        request_data = json.loads(body) if body else {}
        
        # Get headers
        headers = dict(request.headers)
        
        # Forward to OpenAI API
        target_url = f"{OPENAI_API_URL}/v1/{path}"
        
        # Prepare headers for OpenAI
        proxy_headers = {
            "Authorization": headers.get("authorization"),
            "Content-Type": "application/json"
        }
        
        # Remove None values
        proxy_headers = {k: v for k, v in proxy_headers.items() if v is not None}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                target_url,
                json=request_data,
                headers=proxy_headers
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.post("/test-anthropic")
async def test_anthropic(request: Request):
    """Test endpoint for Anthropic API"""
    try:
        headers = dict(request.headers)
        api_key = headers.get("x-api-key")
        
        if not api_key:
            return JSONResponse(
                status_code=400,
                content={"error": "No API key provided"}
            )
        
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ANTHROPIC_API_URL}/v1/messages",
                json=test_data,
                headers=proxy_headers
            )
            
            response_text = response.text
            return {
                "status": response.status_code,
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/test-openai")
async def test_openai(request: Request):
    """Test endpoint for OpenAI API"""
    try:
        headers = dict(request.headers)
        api_key = headers.get("authorization")
        
        if not api_key:
            return JSONResponse(
                status_code=400,
                content={"error": "No API key provided"}
            )
        
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENAI_API_URL}/v1/chat/completions",
                json=test_data,
                headers=proxy_headers
            )
            
            response_text = response.text
            return {
                "status": response.status_code,
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# For Digital Ocean Functions
def main(request):
    """Main function for Digital Ocean Functions"""
    from fastapi import Request
    from fastapi.responses import Response
    
    # This would need to be adapted for the specific Digital Ocean Functions format
    # The exact implementation depends on the Digital Ocean Functions runtime
    pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port) 