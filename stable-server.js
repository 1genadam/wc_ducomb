#!/usr/bin/env node
/**
 * Stable WC Ducomb Server - Simplified without proxy
 * Serves the chat interface directly with better error handling
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
const net = require('net');

const app = express();
const PORT = process.env.PORT || 2000;

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Health check endpoint with network detection
app.get('/health', (req, res) => {
    const checkIBMConnection = () => {
        return new Promise((resolve) => {
            const socket = new net.Socket();
            socket.setTimeout(2000);
            socket.on('connect', () => {
                socket.destroy();
                resolve(true);
            });
            socket.on('timeout', () => {
                socket.destroy();
                resolve(false);
            });
            socket.on('error', () => {
                resolve(false);
            });
            socket.connect(23, '10.0.0.7');
        });
    };
    
    checkIBMConnection().then(canConnect => {
        res.json({
            status: 'healthy',
            service: 'WC Ducomb Stable Server',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            network_status: canConnect ? 'OFFICE' : 'REMOTE',
            ibm_i_accessible: canConnect,
            python_api: 'http://localhost:5001'
        });
    }).catch(() => {
        res.json({
            status: 'healthy',
            service: 'WC Ducomb Stable Server',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            network_status: 'UNKNOWN',
            ibm_i_accessible: false,
            python_api: 'http://localhost:5001'
        });
    });
});

// Direct API proxy route with better error handling  
app.post('/api/inventory/lookup', async (req, res) => {
    try {
        const { default: fetch } = await import('node-fetch');
        console.log(`API Request: Looking up SKU ${req.body.sku}`);
        
        const response = await fetch('http://localhost:5001/api/inventory/lookup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(req.body),
            timeout: 60000 // 60 second timeout
        });

        if (!response.ok) {
            throw new Error(`API responded with status: ${response.status}`);
        }

        const data = await response.json();
        console.log(`API Response: ${data.found ? 'Found' : 'Not found'} - ${req.body.sku}`);
        res.json(data);
        
    } catch (error) {
        console.error('API Error:', error.message);
        res.status(500).json({
            found: false,
            error: true,
            message: 'Backend service unavailable',
            details: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// Serve main routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'inventory-chat-demo.html'));
});

app.get('/local', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'local-chat.html'));
});

app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.url} not found`,
        available_routes: [
            'GET /',
            'GET /local', 
            'GET /admin',
            'GET /health',
            'POST /api/inventory/lookup'
        ]
    });
});

// Error handler
app.use((error, req, res, next) => {
    console.error('Server Error:', error);
    res.status(500).json({
        error: 'Internal Server Error',
        message: 'Something went wrong',
        timestamp: new Date().toISOString()
    });
});

// Graceful shutdown handling
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

// Start server
const server = app.listen(PORT, () => {
    console.log('🚀 WC Ducomb Stable Server Starting...');
    console.log(`📡 Server running on http://localhost:${PORT}`);
    console.log('🔗 Python API Backend: http://localhost:5001');
    console.log('📊 Available Routes:');
    console.log('   GET  /local                - Enhanced Chat Interface');
    console.log('   GET  /                     - Demo Chat Widget');
    console.log('   GET  /admin                - Admin Dashboard');
    console.log('   GET  /health               - Health Check');
    console.log('   POST /api/inventory/lookup - Direct API Call');
    console.log('');
    console.log('✅ Stable server ready for connections');
    console.log('💡 Main interface: http://localhost:2000/local');
});

server.timeout = 65000; // 65 second timeout
server.keepAliveTimeout = 65000;
server.headersTimeout = 66000;