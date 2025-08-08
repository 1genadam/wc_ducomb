const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 2000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Simple health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        server: 'simple-server'
    });
});

// Serve pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'inventory-chat-demo.html'));
});

app.get('/local', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'local-chat.html'));
});

app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// Simple API proxy for chat endpoint
app.post('/api/chat', async (req, res) => {
    try {
        const { default: fetch } = await import('node-fetch');
        const response = await fetch('http://localhost:5001/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(req.body),
            timeout: 60000 // 60 second timeout
        });
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('API proxy error:', error.message);
        res.status(503).json({
            error: 'Backend service unavailable',
            message: 'The inventory lookup service is currently unavailable. Please try again later.',
            timestamp: new Date().toISOString()
        });
    }
});

const server = app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Chat interface: http://localhost:${PORT}/local`);
    console.log(`Admin dashboard: http://localhost:${PORT}/admin`);
});

// Keep alive
setInterval(() => {
    console.log(`[${new Date().toISOString()}] Server alive on port ${PORT}`);
}, 30000);

module.exports = app;