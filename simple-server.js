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

const server = app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Chat interface: http://localhost:${PORT}/local`);
});

// Keep alive
setInterval(() => {
    console.log(`[${new Date().toISOString()}] Server alive on port ${PORT}`);
}, 30000);

module.exports = app;