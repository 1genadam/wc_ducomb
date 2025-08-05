# Claude Code Prompt for Infor Web Documentation

## Updated Prompt for Claude Code

```
I'm continuing work on an IBM i automation project. The knowledge base is at https://github.com/1genadam/wc_ducomb in the /readme directory. Please review the index.md and infor-order-entry-documentation.md to understand the current context.

**IMPORTANT: Connection and Access Information**
- Target system: 10.0.0.7 (internal IP address)
- This is an IBM i system running Infor Distribution A+ ERP
- HTTP server is confirmed running (from network analysis)
- You need to access this as if you're on the internal network

**Primary Documentation URL:**
http://10.0.0.7/APLUS/HLP1003/OEM/HTML5/index.htm

**URL Structure Analysis:**
Based on discovered patterns, the documentation uses this structure:
- Base: http://10.0.0.7/APLUS/HLP1003/OEM/HTML5/
- Index: index.htm with anchor navigation
- Module pattern: APLUS_[MODULE]/[TOPIC]/[SUBTOPIC].htm
- Modules likely include: OE (Order Entry), IM (Inventory), AR (Accounts Receivable), AP (Accounts Payable), GL (General Ledger), PO (Purchasing)

**If Initial URL Fails:**
Try these alternative approaches:
1. http://10.0.0.7/ (root web directory)
2. http://10.0.0.7/APLUS/ (application directory)
3. http://10.0.0.7/APLUS/HLP1003/ (help system directory)
4. Use curl or similar to test connectivity first

**Documentation Strategy:**
1. **Start with connectivity test** - Verify you can reach the server
2. **Map the web structure** - Document available directories and files
3. **Identify all modules** - Look for module identifiers beyond just OE
4. **Focus on technical content** - API docs, database schemas, integration guides
5. **Document systematically** - Create organized markdown files

**Key Areas to Investigate:**
- **Module documentation** for each Infor component (we have OE, need others)
- **API or web service documentation** (look for /api/, /services/, /rest/ paths)
- **Database schema information** (table structures, relationships)
- **Integration guides** (EDI, email, external system interfaces)
- **Configuration documentation** (setup and customization guides)

**Create these documents in /readme directory:**
- infor-web-[module]-documentation.md (for each module found)
- infor-api-discovery.md (if APIs are found)
- infor-database-schema.md (if schema info is available)
- infor-integration-capabilities.md (interface documentation)

**Follow established format:**
- Update /readme/index.md with new documents
- Cross-reference related documents
- Include automation opportunities in each document
- Document URLs and navigation paths
- Note any technical specifications or requirements

**If Access Issues:**
- Document what you tried and what failed
- Note any error messages or HTTP response codes
- Try alternative connection methods
- Report back on connectivity status

**Goal:** Build comprehensive technical documentation of the Infor web system to enable automation development and integration planning. Focus on actionable technical information rather than user guide content.

Start with basic connectivity testing, then systematically explore and document the available web-based resources.
```

## Key Improvements in This Prompt

### **Connection Guidance**
- ✅ Explicit internal IP information
- ✅ System context (IBM i with Infor)
- ✅ Alternative URLs to try if main one fails
- ✅ Connectivity testing approach

### **URL Structure Understanding**
- ✅ Based on the complex anchor-based navigation you discovered
- ✅ Module naming patterns (OE, IM, AR, AP, GL, PO)
- ✅ Directory structure analysis

### **Systematic Approach**
- ✅ Start with connectivity test
- ✅ Map structure before diving deep
- ✅ Focus on technical vs. user documentation
- ✅ Organized documentation strategy

### **Specific Deliverables**
- ✅ Clear file naming convention
- ✅ Integration with existing knowledge base
- ✅ Focus on automation opportunities

This should give Claude Code much better guidance for accessing and documenting your Infor web system!
