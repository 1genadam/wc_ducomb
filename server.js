#!/usr/bin/env node
/**
 * WC Ducomb Inventory Chat Widget - Frontend Server
 * Serves static files and proxies API requests to Python backend
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const API_PORT = process.env.API_PORT || '5001';
const API_BASE_URL = process.env.API_BASE_URL || `http://localhost:${API_PORT}`;

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Proxy API requests to Python backend
app.use('/api', createProxyMiddleware({
    target: API_BASE_URL,
    changeOrigin: true,
    timeout: 60000, // 60 second timeout
    proxyTimeout: 60000,
    onError: (err, req, res) => {
        console.error('Proxy error:', err.message);
        res.status(503).json({
            error: 'Backend service unavailable',
            message: 'The inventory lookup service is currently unavailable. Please try again later.',
            timestamp: new Date().toISOString()
        });
    },
    onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxy request: ${req.method} ${req.url} -> ${API_BASE_URL}${req.url}`);
    },
    onProxyRes: (proxyRes, req, res) => {
        console.log(`Proxy response: ${proxyRes.statusCode} for ${req.method} ${req.url}`);
    }
}));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'WC Ducomb Inventory Frontend',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: require('./package.json').version || '1.0.0'
    });
});

// Serve inventory chat demo as default page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'inventory-chat-demo.html'));
});

// Serve admin dashboard
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Path ${req.path} not found`,
        timestamp: new Date().toISOString()
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred',
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
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log('🚀 WC Ducomb Inventory Frontend Server Starting...');
    console.log(`📡 Server running on http://localhost:${PORT}`);
    console.log(`🔗 API Backend: ${API_BASE_URL}`);
    console.log('📊 Routes available:');
    console.log('   GET  /                    - Inventory Chat Demo');
    console.log('   GET  /admin               - Admin Dashboard');
    console.log('   GET  /health              - Health Check');
    console.log('   ALL  /api/*               - Proxied to Backend');
    console.log('');
    console.log('✅ Server ready for connections');
});

module.exports = app;