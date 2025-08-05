# RPG/COBOL vs. Bypassing Infor A+ - Strategic Analysis

## The Strategic Question: Why Not Bypass Infor Entirely?

**Date:** 2025-08-05  
**Context:** Exploring direct IBM i programming vs. working within Infor framework  
**Question:** Why use RPG/COBOL within Infor's system instead of bypassing it entirely?

## 🎯 The Core Trade-Off

### **Option A: Work Within Infor's Framework**
- Use RPG/COBOL programs that call Infor's business logic
- Access data through Infor's approved methods
- Maintain Infor's business rules and validations

### **Option B: Bypass Infor Entirely**
- Write RPG/COBOL programs that access raw database tables directly
- Bypass Infor's business logic layer
- Direct database manipulation without Infor involvement

## 🔍 Why the "Bypass" Approach is Tempting

### **Apparent Advantages:**
- **Direct database access** - No Infor permission restrictions
- **Full control** - Complete access to all tables and data
- **Performance** - No overhead from Infor's business logic
- **Flexibility** - Can create any business rules you want
- **Independence** - Not limited by Infor's capabilities

### **Immediate Appeal:**
```rpg
// Bypass Infor - Direct database access
// This LOOKS simpler and more powerful
READ ITEMMAST %KEY(itemNumber);
IF %FOUND(ITEMMAST);
   quantity = ITEM_QTY_ONHAND;
   available = ITEM_QTY_AVAIL;
ENDIF;
```

## ⚠️ Why Bypassing Infor is Extremely Dangerous

### **1. Business Logic Corruption**
**The Problem:** Infor A+ contains **thousands of business rules** you can't see:

#### **Hidden Complexities in "Simple" Inventory:**
- **Multi-location calculations** - How quantities are allocated across warehouses
- **Reserved inventory** - Stock allocated to pending orders
- **Lot/serial tracking** - Batch-specific inventory management
- **Unit of measure conversions** - Different units for same item
- **Costing methods** - FIFO, LIFO, standard cost calculations
- **Allocation priorities** - Customer-specific inventory reservations
- **Cross-docking logic** - Direct supplier-to-customer flows
- **Seasonal adjustments** - Time-based inventory calculations

#### **Real-World Example:**
```rpg
// What you think inventory lookup does:
quantity = get_quantity_onhand(item);

// What Infor actually does (simplified):
base_qty = get_physical_quantity(item);
allocated_qty = sum_all_allocations(item);
reserved_qty = get_customer_reservations(item);
pending_receipts = get_inbound_shipments(item);
lot_restrictions = check_lot_availability(item);
location_transfers = get_pending_transfers(item);
seasonal_adjustments = apply_seasonal_factors(item);
available_qty = calculate_complex_availability(
    base_qty, allocated_qty, reserved_qty, 
    pending_receipts, lot_restrictions, 
    location_transfers, seasonal_adjustments
);
```

### **2. Data Integrity Disasters**
**Direct database manipulation bypasses:**
- **Referential integrity** - Cascading updates and deletes
- **Transaction management** - Multi-table consistency
- **Audit trails** - Who changed what and when
- **Validation rules** - Data format and business rule checks
- **Workflow triggers** - Automated processes that should fire

### **3. Compliance and Audit Failures**
**Enterprise Requirements:**
- **SOX compliance** - All financial data changes must be auditable
- **Industry regulations** - FDA, SEC, etc. require controlled access
- **Internal audits** - Changes must go through approved processes
- **Data governance** - Unauthorized access violates policies

### **4. Support and Maintenance Nightmares**
**Long-term Consequences:**
- **Vendor support void** - Infor won't support modified systems
- **Upgrade impossibility** - Custom changes prevent Infor updates
- **Knowledge dependency** - Only you understand the custom code
- **Bug liability** - You own all problems with bypassed logic

## 🎯 Why RPG/COBOL Within Infor's Framework Works

### **The Smart Approach: Work WITH Infor**
```rpg
// Professional approach - Use Infor's business logic
CALLP GetItemAvailability(
    itemNumber : warehouse : 
    quantityOnHand : quantityAvailable : 
    quantityAllocated : errorCode
);

// Export results to accessible table/file
WRITE INVENTORY_EXPORT_RECORD;
```

### **Advantages of Working Within Framework:**
- **Maintains business rules** - All Infor logic still applies
- **Preserves data integrity** - No corruption risk
- **Keeps audit trails** - All changes properly logged
- **Vendor support intact** - Infor still supports the system
- **Future upgrades possible** - System remains upgradeable
- **Compliance maintained** - Meets all regulatory requirements

## 💡 The Professional Integration Pattern

### **Recommended Architecture:**
```
Web Application
    ↕ (API calls)
Custom RPG/COBOL Programs
    ↕ (Calls Infor procedures)
Infor Distribution A+ Business Logic
    ↕ (Controlled database access)
DB2 Database Tables
```

### **Implementation Strategy:**
1. **Create RPG/COBOL programs** that call Infor's existing procedures
2. **Export data** to temporary tables or files accessible via SQL
3. **Access exported data** via JDBC for web applications
4. **Maintain all business integrity** while gaining programmatic access

## 🏗️ Practical Implementation Examples

### **Safe Inventory Access Program:**
```rpg
**FREE
// Professional approach - calls Infor's inventory procedures

DCL-PROC GetInventoryForAPI;
  DCL-PI *N;
    itemNumber CHAR(20) CONST;
  END-PI;

  // Call Infor's official inventory procedure
  CALLP APLUS_GET_ITEM_AVAILABILITY(
    itemNumber : warehouse : 
    qtyOnHand : qtyAvailable : qtyAllocated : 
    returnCode : errorMessage
  );

  // Export to SQL-accessible table
  IF returnCode = *ZEROS;
    inventory_export.item_number = itemNumber;
    inventory_export.qty_onhand = qtyOnHand;
    inventory_export.qty_available = qtyAvailable;
    inventory_export.export_timestamp = %TIMESTAMP();
    
    WRITE INVENTORY_EXPORT inventory_export;
  ENDIF;

END-PROC;
```

### **Web API Access:**
```sql
-- Now accessible via JDBC
SELECT item_number, qty_onhand, qty_available, export_timestamp
FROM QGPL.INVENTORY_EXPORT 
WHERE item_number = 'DGE037700'
  AND export_timestamp >= CURRENT_TIMESTAMP - 1 HOURS;
```

## 🎯 Strategic Recommendation

### **The Hybrid Approach - Best of Both Worlds:**

#### **Phase 1: Screen Scraping (Immediate)**
- Start with screen automation for quick wins
- Prove business value and build credibility
- No system changes required

#### **Phase 2: Professional Integration (Long-term)**
- Create RPG/COBOL programs that work WITH Infor
- Call Infor's business procedures and export results
- Maintain all business integrity and compliance

#### **Phase 3: Official APIs (Future)**
- Research Infor's official web services
- Implement proper API-based integration
- Achieve enterprise-grade integration

## ⚠️ Warning: The Temptation vs. Reality

### **The Temptation:**
"Let's just bypass all this Infor complexity and go direct to the database!"

### **The Reality:**
- **Infor spent millions** developing those business rules
- **Your company chose Infor** specifically for that business logic
- **Enterprise systems are complex** for important business reasons
- **Shortcuts lead to disasters** in mission-critical systems

## 🎯 Bottom Line

### **Why Work Within the Framework:**
- **Preserves your investment** in Infor Distribution A+
- **Maintains business integrity** and compliance
- **Keeps vendor support** and upgrade paths
- **Reduces long-term risk** and maintenance burden
- **Enables sustainable growth** and enhancement

### **The Professional Path:**
Use RPG/COBOL to **extend** Infor's capabilities, not **replace** them. Call Infor's procedures, respect its business logic, and export results in ways that maintain system integrity.

## Document Status
- **Created:** 2025-08-05
- **Context:** Strategic analysis of integration approaches
- **Recommendation:** Work within Infor framework, not around it
- **Rationale:** Preserve business logic, maintain compliance, ensure sustainability

## Notes for Future Sessions
The desire to bypass ERP systems is common but extremely dangerous. Professional integration means working WITH the system's business logic, not around it. The short-term pain of working within constraints pays massive long-term dividends in system stability, compliance, and maintainability.
