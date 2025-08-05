# Claude Code READ-ONLY 5250 Protocol Testing Prompt

## ⚠️ CRITICAL: READ-ONLY TESTING ONLY - NO SYSTEM MODIFICATIONS

```
I'm continuing work on an IBM i automation project with confirmed JDBC connectivity to system 10.0.0.7 (S7891490). The knowledge base is at https://github.com/1genadam/wc_ducomb in the /readme directory.

**🔒 MANDATORY READ-ONLY RESTRICTIONS:**

**ABSOLUTELY FORBIDDEN:**
- ❌ NO database writes, updates, inserts, or deletes
- ❌ NO system configuration changes
- ❌ NO file creation or modification on IBM i system
- ❌ NO user account modifications
- ❌ NO system settings changes
- ❌ NO program installations on IBM i
- ❌ NO data modifications of any kind

**PERMITTED READ-ONLY OPERATIONS:**
- ✅ Connect and authenticate only
- ✅ Navigate menus (inquiry functions only)
- ✅ Read/view data from inquiry screens
- ✅ Test screen navigation paths
- ✅ Extract displayed information
- ✅ Test connection and disconnection
- ✅ Document findings and observations

**TESTING OBJECTIVE:**
Test direct 5250 protocol Python libraries for READ-ONLY inventory inquiry access, specifically testing whether we can programmatically replicate the manual Item Inquiry process without any system modifications.

**SYSTEM CONTEXT:**
- System: IBM i 10.0.0.7 (S7891490) - Production Infor Distribution A+ system
- User: ROBERT with TECH password - Limited inquiry access only
- Manual Process: User can successfully view inventory via 5250 Item Inquiry
- Goal: Replicate this READ-ONLY inquiry process programmatically

**LIBRARIES TO TEST (Priority Order):**

**1. p5250 Library (Primary)**
- Install: pip install p5250
- Purpose: Test pure 5250 protocol connectivity for read-only operations
- Dependencies: May require s3270 utility

**2. tn5250 Python Bindings (Secondary)**
- Alternative 5250 protocol implementation
- Test only if p5250 unavailable or non-functional

**READ-ONLY TESTING PHASES:**

**Phase 1: Safe Connection Testing**
1. Install chosen 5250 library in isolated environment
2. Test basic connection to 10.0.0.7:23 (TN5250 port)
3. Authenticate with ROBERT/TECH credentials
4. Verify successful login without making changes
5. Test clean disconnection
6. Document connection process and any error messages

**Phase 2: READ-ONLY Navigation Testing**
1. Connect and navigate to main Infor menu (view only)
2. Navigate to Inventory menu (option 14) - INQUIRY ONLY
3. Access Item Inquiry function (option 1) - READ-ONLY
4. Test screen recognition and validation
5. Navigate back to main menu
6. Test logout/disconnect process

**Phase 3: READ-ONLY Data Extraction**  
1. Navigate to Item Inquiry screen
2. Enter test SKU: DGE037700 (READ-ONLY lookup)
3. Extract displayed inventory information:
   - Quantity on hand (READ-ONLY)
   - Available quantity (READ-ONLY)
   - Item description (READ-ONLY)
   - Location/warehouse info (READ-ONLY)
4. Test with non-existent SKU for error handling
5. Document exact screen layouts and data positions

**Phase 4: READ-ONLY API Development**
1. Create Python class for read-only inventory lookups
2. Implement connection management (connect/disconnect only)
3. Create inquiry-only methods
4. Test multiple sequential read-only lookups
5. Implement proper error handling for inquiry failures

**SAFETY MEASURES:**

**Connection Safety:**
- Use separate test connection for each test
- Always disconnect cleanly after each test
- Never leave connections open
- Monitor connection count to avoid system impact

**Navigation Safety:**
- Only use inquiry/display functions
- Avoid any maintenance or update menus
- If unsure about a menu option, skip it
- Document safe navigation paths only

**Data Safety:**
- Only read/view data, never modify
- Only use SELECT/INQUIRY type operations
- Avoid any screens that might allow data entry
- Test with known safe data (existing SKU DGE037700)

**ERROR HANDLING:**
- If any operation seems like it might modify data: STOP immediately
- If screens appear unfamiliar: disconnect and document
- If system prompts for confirmations: cancel and exit
- Document all error conditions encountered

**REQUIRED DELIVERABLES:**

**Documentation (All Read-Only Findings):**
- **read-only-5250-protocol-testing.md** - Complete safe testing results
- **safe-5250-navigation-guide.md** - Documented read-only paths only
- **inventory-inquiry-api-readonly.md** - Read-only implementation examples
- **5250-safety-protocols.md** - Safe testing procedures and limitations

**Code Examples (Read-Only Only):**
```python
class ReadOnlyInforInquiry:
    def __init__(self):
        self.connection = None
    
    def connect_readonly(self):
        # Connect for inquiry only
        pass
    
    def lookup_inventory_readonly(self, sku):
        # Read-only inventory lookup
        # Returns data without any modifications
        pass
    
    def disconnect_safely(self):
        # Clean disconnect
        pass
```

**Success Criteria:**
- Establish read-only 5250 protocol connection
- Navigate safely to Item Inquiry without modifications
- Extract inventory data for SKU DGE037700 (read-only)
- Create reusable read-only inventory inquiry API
- Document safe procedures and any limitations discovered

**Failure Criteria:**
- Any attempt to modify system data
- Inability to establish safe read-only connection
- Navigation errors that could impact system
- Any system changes or modifications detected

**PRODUCTION SYSTEM AWARENESS:**
This is a PRODUCTION Infor Distribution A+ system in active use. All testing must be:
- Minimal impact on system performance
- Read-only operations exclusively
- Quick connection/disconnection cycles
- No interference with business operations
- Professional and safe testing practices

**DOCUMENTATION REQUIREMENTS:**
- Include exact commands that work safely
- Document all safe navigation paths
- Provide clear warnings about unsafe operations
- Include error handling for safe disconnection
- Create troubleshooting guide for read-only issues

**IF TESTING REVEALS UNSAFE CONDITIONS:**
- Stop testing immediately
- Document the unsafe condition
- Recommend screen scraping as safer alternative
- Do not proceed with questionable operations

**COMPARISON FRAMEWORK:**
Compare read-only 5250 protocol approach against:
1. Manual inquiry process (our baseline)
2. Screen scraping automation (our planned fallback)
3. Limited JDBC database access (our confirmed approach)

Focus on safety, reliability, and read-only data access capabilities.

The goal is to safely determine if direct 5250 protocol can provide read-only inventory inquiry without any risk to the production system.

Update documentation with findings and maintain focus on read-only operations throughout.
```

## 🔒 Key Safety Emphasis

### **Mandatory Read-Only Restrictions:**
- ❌ **NO database writes, updates, inserts, or deletes**
- ❌ **NO system configuration changes**  
- ❌ **NO file creation or modification**
- ❌ **NO user account modifications**
- ❌ **NO system settings changes**

### **Permitted Operations:**
- ✅ **Connect and authenticate only**
- ✅ **Navigate inquiry menus only**
- ✅ **Read/view data from displays**
- ✅ **Extract displayed information**
- ✅ **Test connection/disconnection**

### **Safety Protocols:**
- **If any operation might modify data: STOP immediately**
- **Use separate test connections**
- **Always disconnect cleanly**
- **Document safe navigation paths only**
- **Avoid maintenance or update menus**

## 🎯 **This Read-Only Testing Will Determine:**

### **If Safe Read-Only 5250 Protocol Works:**
- ✅ Skip screen recording entirely
- ✅ Direct protocol-level inquiry access
- ✅ Better performance than screen scraping
- ✅ More reliable automation foundation

### **If Unsafe or Non-Functional:**
- ✅ Fall back to screen scraping approach
- ✅ Document why protocol access isn't viable
- ✅ Maintain production system safety

## 📋 **Ready for Safe Testing**

The prompt above provides **comprehensive read-only testing instructions** that will safely evaluate direct 5250 protocol access without any risk to your production Infor system.

**Copy the complete prompt above** and give it to Claude Code for safe, read-only testing of direct 5250 protocol libraries.

This will definitively answer whether we can safely skip screen recording and go directly to protocol-level automation! 🔒🚀
