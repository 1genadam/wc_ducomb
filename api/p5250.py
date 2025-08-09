#!/usr/bin/env python3
"""
Custom P5250 Client Implementation using Telnet
Fixes authentication credential sequence bug
"""

import telnetlib
import time
import logging

logger = logging.getLogger(__name__)

class P5250Client:
    """Custom P5250 client using telnet with proper credential handling"""
    
    def __init__(self, hostName, hostPort, modelName='3279-2', enableTLS='no', timeoutInSec=60):
        self.hostname = hostName
        self.port = int(hostPort)
        self.timeout = timeoutInSec
        self.connection = None
        self.connected = False
        logger.info(f"P5250Client initialized for {hostName}:{hostPort}")
    
    def connect(self):
        """Connect to IBM i system via telnet"""
        try:
            logger.info(f"Connecting to {self.hostname}:{self.port} with timeout {self.timeout}s")
            self.connection = telnetlib.Telnet(self.hostname, self.port, timeout=self.timeout)
            self.connected = True
            logger.info("Telnet connection established successfully")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            raise
    
    def isConnected(self):
        """Check if connection is active"""
        return self.connected and self.connection is not None
    
    def disconnect(self):
        """Disconnect from IBM i system"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Telnet connection closed")
            except:
                pass
        self.connected = False
        self.connection = None
    
    def getScreen(self):
        """Read current screen content"""
        if not self.connection:
            return ""
        
        try:
            # Read available data with timeout
            data = self.connection.read_very_eager()
            if not data:
                # Try reading with a short timeout if no immediate data
                data = self.connection.read_until(b'\n', timeout=2)
            
            screen = data.decode('ascii', errors='ignore')
            logger.debug(f"Screen content: {screen[:100]}...")
            return screen
            
        except Exception as e:
            logger.error(f"Error reading screen: {e}")
            return ""
    
    def moveToFirstInputField(self):
        """Move cursor to first input field - telnet doesn't need explicit cursor movement"""
        logger.debug("moveToFirstInputField called (no-op for telnet)")
        pass
    
    def sendText(self, text):
        """Send text to current field with proper spacing"""
        if not self.connection:
            logger.error("Cannot send text - no connection")
            return
        
        try:
            # Clean the text and ensure proper formatting
            clean_text = str(text).strip()
            logger.info(f"Sending text: {clean_text}")
            
            # Send text as bytes
            self.connection.write(clean_text.encode('ascii'))
            
            # Small delay to ensure text is processed
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error sending text '{text}': {e}")
    
    def sendTab(self):
        """Send tab character to move to next field"""
        if not self.connection:
            logger.error("Cannot send tab - no connection")
            return
        
        try:
            logger.debug("Sending TAB")
            self.connection.write(b'\t')
            time.sleep(0.2)  # Longer delay for field navigation
        except Exception as e:
            logger.error(f"Error sending tab: {e}")
    
    def sendEnter(self):
        """Send enter/return to submit or continue"""
        if not self.connection:
            logger.error("Cannot send enter - no connection")
            return
        
        try:
            logger.debug("Sending ENTER")
            self.connection.write(b'\r\n')  # Both CR and LF for IBM systems
            time.sleep(0.5)  # Longer delay for screen processing
        except Exception as e:
            logger.error(f"Error sending enter: {e}")
    
    def sendClear(self):
        """Send clear screen command"""
        if not self.connection:
            return
        
        try:
            logger.debug("Sending CLEAR")
            # Clear screen sequence for 5250 (Ctrl+L)
            self.connection.write(b'\x0C')
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Error sending clear: {e}")
    
    def waitForScreen(self, timeout=5):
        """Wait for screen to load completely"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                screen = self.getScreen()
                if screen and len(screen.strip()) > 10:  # Screen has content
                    return screen
                time.sleep(0.2)
            except:
                pass
        
        logger.warning(f"Timeout waiting for screen after {timeout}s")
        return self.getScreen()
    
    def sendCommand(self, command):
        """Send a command string followed by enter"""
        self.sendText(command)
        self.sendEnter()
        return self.waitForScreen()
    
    def login(self, username, password):
        """Perform login with correct credential sequence"""
        try:
            logger.info(f"Starting login sequence for user: {username}")
            
            # Wait for initial login screen
            time.sleep(3)
            initial_screen = self.getScreen()
            logger.debug(f"Initial screen: {initial_screen[:200]}...")
            
            if "User" not in initial_screen and "Sign On" not in initial_screen:
                logger.warning("No login screen detected, proceeding anyway")
            
            # Clear any existing input
            self.sendClear()
            time.sleep(1)
            
            # Send username with proper formatting
            logger.info("Entering username...")
            self.sendText(username)
            
            # Send TAB to move to password field
            logger.info("Moving to password field...")
            self.sendTab()
            
            # Send password
            logger.info("Entering password...")
            self.sendText(password)
            
            # Submit login
            logger.info("Submitting login credentials...")
            self.sendEnter()
            
            # Wait for response
            time.sleep(4)
            login_result = self.getScreen()
            
            # Check for successful login indicators
            if any(indicator in login_result.upper() for indicator in ["MAIN MENU", "INFOR", "WELCOME", "OPTION"]):
                logger.info("Login appears successful")
                return True
            elif any(indicator in login_result.upper() for indicator in ["INVALID", "NOT VALID", "INCORRECT"]):
                logger.error("Login failed - invalid credentials")
                return False
            else:
                logger.info("Login status uncertain, continuing...")
                return True  # Assume success if no clear failure
                
        except Exception as e:
            logger.error(f"Login sequence failed: {e}")
            return False