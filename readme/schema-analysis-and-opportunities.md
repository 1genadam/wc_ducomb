# Discovered Schema Analysis and Capabilities

## Schema Discovery Results Analysis

**Date:** 2025-08-05  
**Discovered:** 18+ APLUS-related schemas  
**Status:** Available for exploration and potential access

## 🗂️ Complete Schema Inventory

### **Primary Schemas**
- **APLUS** - Main Infor Distribution A+ schema (likely core tables)
- **APLUSNCVT** - Data conversion schema (setup/migration related)
- **QGPL** - General purpose library (shared system resources)

### **Version-Specific Schemas**
- **APLUS10** - Version 10 core schema
- **APLUS13** - Version 13 core schema

### **Component-Specific Schemas (Version 10)**
- **APLUS10C** - Version 10 Core components
- **APLUS10CSV** - CSV/Import-Export functionality
- **APLUS10FDC** - File Distribution/Control
- **APLUS10FTS** - Full Text Search capabilities
- **APLUS10M** - Manufacturing/Production components
- **APLUS10MDC** - Master Data Control
- **APLUS10MTS** - Make-to-Stock functionality

### **Component-Specific Schemas (Version 13)**
- **APLUS13C** - Version 13 Core components
- **APLUS13CSV** - CSV/Import-Export functionality
- **APLUS13FDC** - File Distribution/Control
- **APLUS13FTS** - Full Text Search capabilities
- **APLUS13M** - Manufacturing/Production components
- **APLUS13MDC** - Master Data Control
- **APLUS13MTS** - Make-to-Stock functionality

### **Additional Schema**
- **APLUS2AX** - Likely Microsoft Dynamics AX integration or legacy conversion

## 🔍 What We Can Potentially Access

### **1. System Configuration Tables**
These schemas likely contain tables we **can** access:

#### **Probable Accessible Tables:**
- **System parameters** and configuration settings
- **User setup** and preference tables
- **Code tables** (status codes, type codes, etc.)
- **Reference data** (states, countries, units of measure)
- **Menu and security** configuration
- **Report definitions** and layouts

#### **Why These Might Be Accessible:**
- Non-sensitive reference data
- System administration information
- Configuration parameters
- Static lookup tables

### **2. Import/Export Capabilities (CSV Schemas)**
The **APLUS10CSV** and **APLUS13CSV** schemas suggest:

#### **Potential Capabilities:**
- **Data import/export functions** already built into Infor
- **CSV processing tables** for bulk operations  
- **Interface tables** for external system integration
- **Staging areas** for data validation

#### **Automation Opportunities:**
- Use Infor's built-in import/export mechanisms
- Access staging tables for data exchange
- Leverage existing ETL functionality

### **3. Full Text Search (FTS Schemas)**
The **FTS (Full Text Search)** schemas indicate:

#### **Search Capabilities:**
- **Indexed search data** across business documents
- **Search result tables** with item/customer references
- **Query history** and search analytics
- **Document indexing** information

#### **Integration Potential:**
- Build custom search interfaces
- Access search indices for quick lookups
- Create search-based applications

## 🧪 Testing Strategy for Schema Access

### **SQL Scripts to Test Each Schema**

Let me create targeted queries to test what we can actually access:

```sql
-- Test 1: Check accessible tables in each schema
SELECT TABLE_SCHEMA, COUNT(*) as TABLE_COUNT
FROM QSYS2.SYSTABLES 
WHERE TABLE_SCHEMA IN ('APLUS', 'APLUS10', 'APLUS13', 'APLUS10CSV', 'APLUS13CSV', 'APLUS10FTS', 'APLUS13FTS')
  AND TABLE_TYPE = 'T'
GROUP BY TABLE_SCHEMA
ORDER BY TABLE_SCHEMA;

-- Test 2: Look for reference/configuration tables
SELECT TABLE_SCHEMA, TABLE_NAME
FROM QSYS2.SYSTABLES
WHERE TABLE_SCHEMA LIKE '%APLUS%'
  AND TABLE_TYPE = 'T'
  AND (TABLE_NAME LIKE '%CODE%' 
    OR TABLE_NAME LIKE '%REF%'
    OR TABLE_NAME LIKE '%CONFIG%'
    OR TABLE_NAME LIKE '%SETUP%'
    OR TABLE_NAME LIKE '%PARAM%'
    OR TABLE_NAME LIKE '%MENU%')
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Test 3: CSV/Import tables
SELECT TABLE_SCHEMA, TABLE_NAME
FROM QSYS2.SYSTABLES
WHERE TABLE_SCHEMA IN ('APLUS10CSV', 'APLUS13CSV')
  AND TABLE_TYPE = 'T'
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Test 4: Full Text Search tables
SELECT TABLE_SCHEMA, TABLE_NAME
FROM QSYS2.SYSTABLES
WHERE TABLE_SCHEMA IN ('APLUS10FTS', 'APLUS13FTS')
  AND TABLE_TYPE = 'T'
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

## 💡 Practical Applications of Discovered Schemas

### **Immediate Opportunities**

#### **1. Configuration Management**
- **Export system settings** for backup/documentation
- **Compare configurations** between environments
- **Track configuration changes** over time
- **Generate system documentation** automatically

#### **2. Reference Data Access**
- **Customer lists** (if accessible)
- **Product categories** and classifications
- **Geographic codes** (states, countries, zip codes)
- **Unit of measure** conversions
- **Currency codes** and exchange rate tables

#### **3. Search and Lookup Services**
- **Build search interfaces** using FTS capabilities
- **Create lookup APIs** for customer service
- **Implement autocomplete** functionality
- **Generate search analytics**

#### **4. Data Integration Platform**
- **Use CSV schemas** for bulk data operations
- **Create ETL processes** using existing infrastructure
- **Build data synchronization** with external systems
- **Implement automated imports/exports**

### **Advanced Integration Scenarios**

#### **1. Business Intelligence Platform**
```sql
-- Example: Customer analysis using accessible reference data
SELECT 
    customer_state,
    COUNT(*) as customer_count,
    AVG(credit_limit) as avg_credit
FROM accessible_customer_table
GROUP BY customer_state;
```

#### **2. System Monitoring**
- **Track system usage** via accessible logs
- **Monitor performance** through system tables
- **Generate health reports** automatically
- **Alert on configuration changes**

#### **3. Custom Applications**
- **Customer service tools** using reference data
- **Mobile lookup apps** for field staff
- **Self-service portals** with available data
- **Reporting dashboards** using accessible metrics

## 🔧 Next Steps to Unlock Schema Potential

### **Phase 1: Discovery Testing**
Run the SQL scripts above to identify:
1. **Which schemas have accessible tables**
2. **What types of data are available**
3. **Which tables contain useful business information**
4. **What permission levels exist**

### **Phase 2: Data Mapping**
For accessible tables:
1. **Document table structures** and relationships
2. **Identify key business data** available
3. **Map data flows** and dependencies
4. **Create data dictionaries** for development

### **Phase 3: Application Development**
Build applications using accessible data:
1. **Reference data APIs** for lookups
2. **Configuration management** tools
3. **Search and discovery** interfaces
4. **Data integration** platforms

## 🎯 Realistic Expectations

### **Likely Accessible:**
- ✅ **System configuration** and parameters
- ✅ **Reference data** and code tables
- ✅ **User preferences** and menu structures
- ✅ **Import/export staging** tables
- ✅ **Search indices** and metadata

### **Likely Protected:**
- ❌ **Transaction data** (orders, invoices)
- ❌ **Financial information** (pricing, costs)
- ❌ **Customer sensitive data** (addresses, contacts)
- ❌ **Inventory quantities** and valuations

### **Unknown Until Tested:**
- ❓ **Master data** (item descriptions, basic customer info)
- ❓ **Historical data** (archived transactions)
- ❓ **Workflow tables** (approvals, status tracking)
- ❓ **Report definitions** and layouts

## 📊 Business Value Potential

Even with limited access, the discovered schemas offer significant automation opportunities:

### **High-Value Applications:**
1. **System administration** tools and dashboards
2. **Reference data** APIs for other applications
3. **Configuration management** and documentation
4. **Search and discovery** interfaces
5. **Data integration** and ETL platforms

### **Foundation for Growth:**
- **Prove value** with accessible data first
- **Build trust** with system administrators
- **Demonstrate ROI** to justify expanded permissions
- **Create foundation** for larger integration projects

## Document Status
- **Created:** 2025-08-05
- **Schemas Analyzed:** 18+ APLUS-related schemas
- **Next Steps:** Run discovery SQL scripts to identify accessible tables
- **Goal:** Maximize value from available data while respecting security boundaries

## Notes for Implementation
The discovered schemas represent a sophisticated Infor Distribution A+ installation with multiple versions and specialized components. Even with limited permissions, significant automation and integration value can be achieved through creative use of accessible system, configuration, and reference data.
