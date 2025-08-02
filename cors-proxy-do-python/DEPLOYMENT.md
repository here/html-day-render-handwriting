# Digital Ocean Functions Deployment

## Files to Upload:
- `do_function.py` - Main function code
- `requirements.txt` - Python dependencies

## Deployment Steps:
1. Go to your Digital Ocean account
2. Navigate to Functions
3. Click "Create Function"
4. Choose Python runtime
5. Upload the files above
6. Set function name: "ocr-proxy"
7. Deploy

## Function URL:
After deployment, you'll get a URL like:
`https://your-function-url.digitalocean.app`

## Testing:
```bash
curl -X POST https://your-function-url.digitalocean.app \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "path": "health",
    "api_type": "anthropic"
  }'
```
