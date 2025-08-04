# Session Continuity Guidelines

## Purpose
This document provides guidelines for maintaining context and progress across multiple Claude chat sessions for the IBM i automation and knowledge base project.

## Repository Structure
- **Primary Repository**: https://github.com/1genadam/wc_ducomb
- **Knowledge Base Location**: `/readme/` directory
- **Index File**: `/readme/index.md`

## Starting a New Claude Session

### Essential Context to Provide
1. **Repository Link**: https://github.com/1genadam/wc_ducomb
2. **Current Project Goals**: Building automation and customer applications for IBM i systems
3. **Key Context**: Working with IBM i Access Client Solutions (ACS)
4. **Session Goal**: Specific objectives for the current session

### Standard Opening Message Template
```
I'm continuing work on an IBM i automation project. The knowledge base is at https://github.com/1genadam/wc_ducomb in the /readme directory. Please review the index.md and relevant documents to understand the current context. My goal for this session is [specific objective].
```

## Documentation Standards

### File Naming Convention
- Use kebab-case for filenames: `ibm-i-acs-overview.md`
- Include creation date in document metadata
- Use descriptive, searchable names

### Document Structure
Each document should include:
- **Overview/Purpose section**
- **Current status/progress**
- **Next steps or action items**
- **Related documents references**
- **Notes for future sessions**
- **Last updated timestamp**

### Content Guidelines
- Write for someone with no prior context
- Include specific technical details and configurations
- Document decisions and reasoning
- Provide examples and code snippets where applicable
- Link to related documents

## Progress Tracking

### Session Log
Maintain a session log in the index.md with:
- Date of session
- Key accomplishments
- Decisions made
- Next priorities

### Version Control
- Commit frequently with descriptive messages
- Tag major milestones
- Include session date in commit messages

## Knowledge Transfer Best Practices

### Context Preservation
1. Always update relevant documents with new information
2. Create new documents for distinct topics
3. Update the index.md with new documents
4. Cross-reference related documents

### Decision Documentation
- Record why certain approaches were chosen
- Document alternatives considered
- Include pros/cons analysis
- Note any constraints or limitations

### Technical Details
- Include specific configurations
- Document command sequences
- Provide error messages and solutions
- Include screenshots or diagrams when helpful

## Project Continuity

### Current Project State
As of 2025-08-04:
- Repository initialized with knowledge base structure
- IBM i ACS documentation completed
- Ready for specific automation development

### Typical Session Flow
1. Review existing documentation
2. Identify specific goals for session
3. Work on development/documentation
4. Update relevant documents
5. Update index with progress
6. Commit changes with descriptive messages

### Handoff Checklist
Before ending a session:
- [ ] All new information documented
- [ ] Index.md updated
- [ ] Changes committed to repository
- [ ] Next steps clearly defined
- [ ] Any blockers or questions noted

## Emergency Context Recovery

If repository access is lost or unclear:
- Primary contact: 1genadam
- Repository: wc_ducomb
- Focus area: IBM i Access Client Solutions automation
- Goal: Build customer applications and automation tools

## Communication Standards

### Technical Terms
- IBM i (not AS/400 or iSeries in new documentation)
- ACS (IBM i Access Client Solutions)
- Use consistent terminology across documents

### Audience Assumptions
- Write for technical users familiar with IBM i systems
- Include explanations for complex automation concepts
- Assume familiarity with basic development practices

## Document Status
- **Created**: 2025-08-04
- **Last Updated**: 2025-08-04
- **Next Review**: After first session transition test

## Notes for Future Sessions
This document itself should be updated based on experience with actual session transitions. Pay attention to what context is most critical for continuity.
