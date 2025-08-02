const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 3001;

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json({ limit: '50mb' }));

// Proxy route for Anthropic API
app.use('/api/anthropic', createProxyMiddleware({
  target: 'https://api.anthropic.com',
  changeOrigin: true,
  pathRewrite: {
    '^/api/anthropic': ''
  },
  onProxyReq: (proxyReq, req, res) => {
    // Forward the original headers
    if (req.headers['x-api-key']) {
      proxyReq.setHeader('x-api-key', req.headers['x-api-key']);
      console.log('API Key found:', req.headers['x-api-key'].substring(0, 10) + '...');
    } else {
      console.log('No API key found in headers');
    }
    if (req.headers['anthropic-version']) {
      proxyReq.setHeader('anthropic-version', req.headers['anthropic-version']);
    }
    if (req.headers['content-type']) {
      proxyReq.setHeader('content-type', req.headers['content-type']);
    }
    
    // Log the request for debugging
    console.log(`Proxying: ${req.method} ${req.url} -> ${proxyReq.path}`);
    console.log('Headers being sent:', proxyReq.getHeaders());
    
    // Log request body size
    if (req.body) {
      console.log('Request body size:', JSON.stringify(req.body).length, 'bytes');
    }
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`Response status: ${proxyRes.statusCode}`);
    console.log('Response headers:', proxyRes.headers);
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    console.error('Error details:', {
      code: err.code,
      errno: err.errno,
      syscall: err.syscall,
      message: err.message
    });
    
    // Send a more helpful error response
    res.status(500).json({ 
      error: 'Proxy error', 
      details: err.message,
      code: err.code,
      suggestion: 'Check your API key and ensure it\'s valid'
    });
  },
  // Add timeout and retry options
  timeout: 30000,
  proxyTimeout: 30000
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'Proxy server is running' });
});

// Test endpoint for Anthropic API
app.post('/test-anthropic', async (req, res) => {
  try {
    const testResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': req.headers['x-api-key'] || 'test-key',
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 10,
        messages: [
          {
            role: "user",
            content: "Hello"
          }
        ]
      })
    });
    
    console.log('Test response status:', testResponse.status);
    const responseText = await testResponse.text();
    console.log('Test response:', responseText);
    
    res.json({
      status: testResponse.status,
      response: responseText.substring(0, 200) + '...'
    });
  } catch (error) {
    console.error('Test error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
  console.log(`Anthropic API proxy available at http://localhost:${PORT}/api/anthropic`);
  console.log('Update your endpoint URL to: http://localhost:3001/api/anthropic');
});

module.exports = app; 