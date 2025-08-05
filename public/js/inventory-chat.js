// WC Ducomb Inventory Lookup Chat System
// Integrates with 5250 protocol for real-time inventory data

class InventoryChatWidget {
    constructor() {
        this.backendAvailable = false;
        this.messages = [];
        this.isLoading = false;
        this.sessionId = this.generateSessionId();
        this.autoReopenDelay = 2 * 60 * 1000; // 2 minutes
        
        // System prompt for inventory lookup
        this.systemPrompt = `You are an AI assistant for WC Ducomb's inventory system. Your PRIMARY function is to help users look up product inventory using SKU numbers via our 5250 protocol automation.

Key capabilities:
- Look up real-time inventory by SKU
- Check stock levels across warehouses
- Provide product descriptions and details
- Check allocated vs available quantities
- View items on purchase order
- Check backorder status

When a user provides a SKU, immediately look it up in the system.
Format: SKU should be alphanumeric (e.g., DGE037700)

IMPORTANT: Always be helpful and guide users to provide SKU numbers for inventory lookups.`;
        
        this.init();
    }

    generateSessionId() {
        return 'inv-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    async init() {
        this.createChatWidget();
        this.bindEvents();
        this.addWelcomeMessage();
        await this.checkBackendStatus();
    }

    createChatWidget() {
        // Create chat widget HTML if it doesn't exist
        if (!document.getElementById('inventory-chat-widget')) {
            const widgetHTML = `
                <div id="inventory-chat-widget" class="hidden fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50">
                    <div class="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                        <h3 class="font-bold">Inventory Lookup Assistant</h3>
                        <button id="close-chat-widget" class="text-white hover:text-gray-200">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="flex-1 overflow-y-auto p-4" id="chat-messages">
                        <!-- Messages will appear here -->
                    </div>
                    <div class="p-4 border-t">
                        <div class="flex space-x-2">
                            <input type="text" 
                                   id="chat-input"
                                   placeholder="Enter SKU (e.g., DGE037700)..." 
                                   class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <button id="send-button" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                Send
                            </button>
                        </div>
                        <div class="mt-2 flex flex-wrap gap-2" id="quick-actions">
                            <button class="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded" data-action="sample">Sample SKU</button>
                            <button class="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded" data-action="help">Help</button>
                            <button class="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded" data-action="status">System Status</button>
                        </div>
                    </div>
                </div>
                
                <button id="chat-widget-button" class="fixed bottom-4 right-4 w-14 h-14 bg-blue-600 rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition-colors z-40">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                    </svg>
                </button>
            `;
            
            document.body.insertAdjacentHTML('beforeend', widgetHTML);
        }
    }

    bindEvents() {
        const chatButton = document.getElementById('chat-widget-button');
        const chatWidget = document.getElementById('inventory-chat-widget');
        const closeButton = document.getElementById('close-chat-widget');
        const messageInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const quickActions = document.getElementById('quick-actions');

        if (chatButton && chatWidget) {
            chatButton.addEventListener('click', () => {
                chatWidget.classList.toggle('hidden');
                if (!chatWidget.classList.contains('hidden')) {
                    messageInput?.focus();
                }
            });
        }

        if (closeButton && chatWidget) {
            closeButton.addEventListener('click', () => {
                chatWidget.classList.add('hidden');
            });
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Quick action buttons
        if (quickActions) {
            quickActions.addEventListener('click', (e) => {
                if (e.target.dataset.action) {
                    this.handleQuickAction(e.target.dataset.action);
                }
            });
        }

        // Auto-open after 10 seconds
        setTimeout(() => {
            const widget = document.getElementById('inventory-chat-widget');
            if (widget && widget.classList.contains('hidden')) {
                widget.classList.remove('hidden');
            }
        }, 10000);
    }

    handleQuickAction(action) {
        switch(action) {
            case 'sample':
                document.getElementById('chat-input').value = 'DGE037700';
                this.sendMessage();
                break;
            case 'help':
                this.addMessage('assistant', 'I can help you look up inventory by SKU. Just type a SKU number (like DGE037700) and I\'ll fetch the current inventory status including quantities, allocations, and backorders.');
                break;
            case 'status':
                this.checkBackendStatus();
                break;
        }
    }

    async checkBackendStatus() {
        try {
            const response = await fetch('/api/inventory/status');
            if (response.ok) {
                const data = await response.json();
                this.backendAvailable = data.available;
                if (data.available) {
                    this.addMessage('system', '✅ Inventory system connected (IBM i: ' + (data.host || '10.0.0.7') + ')');
                } else {
                    this.addMessage('system', '⚠️ Running in demo mode - backend not available');
                }
            }
        } catch (error) {
            this.backendAvailable = false;
            console.log('Backend not available, using demo mode');
        }
    }

    addWelcomeMessage() {
        const welcomeMessage = {
            role: 'assistant',
            content: '👋 Welcome to the WC Ducomb Inventory System!\n\nI can help you look up real-time inventory data. Just provide a SKU number and I\'ll fetch:\n• Current stock levels\n• Available vs allocated quantities\n• Purchase orders and backorders\n• Product descriptions\n\nTry entering a SKU like "DGE037700" to get started!'
        };
        
        this.messages.push(welcomeMessage);
        this.updateChatDisplay();
    }

    addMessage(role, content) {
        this.messages.push({ role, content });
        this.updateChatDisplay();
    }

    async sendMessage() {
        const messageInput = document.getElementById('chat-input');
        if (!messageInput || this.isLoading) return;

        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        // Add user message
        this.addMessage('user', userMessage);
        messageInput.value = '';

        // Show loading
        this.isLoading = true;
        this.showTypingIndicator();

        try {
            // Check if message looks like a SKU
            const skuPattern = /^[A-Z0-9]{6,12}$/i;
            if (skuPattern.test(userMessage)) {
                // Direct SKU lookup
                const response = await this.lookupSKU(userMessage);
                this.addMessage('assistant', response);
            } else {
                // Process through AI for intent detection
                const response = await this.getAIResponse(userMessage);
                this.addMessage('assistant', response);
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('assistant', '❌ Sorry, I encountered an error. Please try again or contact support.');
        } finally {
            this.isLoading = false;
            this.hideTypingIndicator();
        }
    }

    async lookupSKU(sku) {
        if (!this.backendAvailable) {
            // Demo response
            return this.getDemoInventoryResponse(sku);
        }

        try {
            const response = await fetch('/api/inventory/lookup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sku: sku.toUpperCase() })
            });

            if (response.ok) {
                const data = await response.json();
                return this.formatInventoryResponse(data);
            } else {
                return '❌ Could not retrieve inventory for SKU: ' + sku;
            }
        } catch (error) {
            console.error('Inventory lookup error:', error);
            return this.getDemoInventoryResponse(sku);
        }
    }

    formatInventoryResponse(data) {
        if (!data.found) {
            return `❌ SKU ${data.sku} not found in the system.`;
        }

        const emoji = data.net_available > 0 ? '✅' : '⚠️';
        const status = data.net_available > 0 ? 'In Stock' : 'Out of Stock';

        return `${emoji} **Inventory Status for SKU ${data.sku}**\n\n` +
               `📦 **Product:** ${data.description}\n` +
               `🏭 **Warehouse:** ${data.warehouse}\n` +
               `📊 **Status:** ${status}\n\n` +
               `**Quantities:**\n` +
               `• On Hand: ${data.on_hand}\n` +
               `• Allocated: ${data.allocated}\n` +
               `• Available: ${data.net_available}\n` +
               `• On Purchase Order: ${data.on_purchase_order}\n` +
               `• On Back Order: ${data.on_back_order}\n\n` +
               `⏱️ *Retrieved: ${new Date().toLocaleTimeString()}*`;
    }

    getDemoInventoryResponse(sku) {
        // Demo data based on the successful lookup from documentation
        if (sku.toUpperCase() === 'DGE037700') {
            return `✅ **Inventory Status for SKU DGE037700**\n\n` +
                   `📦 **Product:** P2B-SC-100 1SC 123806\n` +
                   `🏭 **Warehouse:** 00\n` +
                   `📊 **Status:** In Stock\n\n` +
                   `**Quantities:**\n` +
                   `• On Hand: 6.000 EA\n` +
                   `• Allocated: 0.000\n` +
                   `• Available: 6.000\n` +
                   `• On Purchase Order: 0.000\n` +
                   `• On Back Order: 0.000\n\n` +
                   `⏱️ *Demo data - backend not connected*`;
        }
        
        // Generic demo response
        return `📊 **Demo Mode** - SKU: ${sku}\n\n` +
               `To see real inventory data, the backend 5250 service needs to be running.\n\n` +
               `Try SKU "DGE037700" for a demo example.`;
    }

    async getAIResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Simple intent detection
        if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
            return 'I can help you look up inventory! Just type a SKU number (like DGE037700) and I\'ll fetch the current stock levels, allocations, and order status.';
        }
        
        if (lowerMessage.includes('example') || lowerMessage.includes('sample')) {
            return 'Here\'s an example SKU you can try: **DGE037700**\n\nJust type it in and press Enter to see the inventory status!';
        }
        
        if (lowerMessage.includes('warehouse')) {
            return 'Our system tracks inventory across multiple warehouses. When you look up a SKU, I\'ll show you the warehouse location and all quantity details.';
        }
        
        // Extract potential SKU from message
        const skuMatch = message.match(/[A-Z0-9]{6,12}/i);
        if (skuMatch) {
            return await this.lookupSKU(skuMatch[0]);
        }
        
        return 'Please provide a SKU number to look up inventory. SKUs are typically 6-12 character codes like "DGE037700". What SKU would you like to check?';
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex mb-4 typing-indicator';
        typingDiv.innerHTML = `
            <div class="bg-gray-200 p-3 rounded-lg max-w-xs">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateChatDisplay() {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        chatMessages.innerHTML = '';

        this.messages.forEach(message => {
            const messageDiv = document.createElement('div');
            messageDiv.className = message.role === 'user' ? 'flex justify-end mb-4' : 'flex mb-4';
            
            const messageContent = document.createElement('div');
            messageContent.className = message.role === 'user' 
                ? 'bg-blue-600 text-white p-3 rounded-lg max-w-xs'
                : message.role === 'system' 
                    ? 'bg-gray-100 text-gray-600 p-3 rounded-lg max-w-xs italic'
                    : 'bg-gray-200 p-3 rounded-lg max-w-xs';
            
            // Handle markdown-style formatting
            const formattedContent = message.content
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            
            messageContent.innerHTML = `<div class="text-sm">${formattedContent}</div>`;
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.inventoryChat = new InventoryChatWidget();
    });
} else {
    window.inventoryChat = new InventoryChatWidget();
}

// Export for use in other contexts
window.InventoryChatWidget = InventoryChatWidget;