# VPA Project Alignment Guide

## Purpose
This document provides guidance for maintaining alignment when creating new VPA planning documents. It outlines where to find key information, how to ensure consistency, and what patterns to follow.

## Key Resources

### Primary Resources
1. **MASTER_LOG.md** - The central tracking document located in `planning_docs/MASTER_LOG.md`
   - Always check this first to identify the next document to create
   - Contains current completion status, priority order, and action log
   - Must be updated after each document creation

2. **Existing Documentation** - Review related completed documents in `planning_docs/` directories
   - Look for consistent patterns, terminology, and structure
   - Reference existing code examples and architectural approaches
   - Ensure technical consistency with existing documentation

3. **Final_Planning_Documents/** - Reference materials and templates
   - Contains more detailed planning materials that serve as sources of truth
   - Particularly useful for understanding integration points between components
   - Provides implementation timelines and technical specifications

## Alignment Process

### Step 1: Identify the Next Document
1. Check `planning_docs/MASTER_LOG.md` for current priority documents
2. Note the specific section where the document belongs (e.g., `3_implementation_roadmap/`)
3. Review the "Next Steps" section to confirm priorities

### Step 2: Research and Gather Information
1. Review related completed documents in the same directory
2. Check `Final_Planning_Documents/` for related reference materials:
   - For implementation roadmaps: `VPA_MASTER_IMPLEMENTATION_PLAN.md`
   - For component specifications: `VPA_COMPONENT_TECHNICAL_ANALYSIS.md`
   - For integration details: `VPA_COMPONENT_INTEGRATION_SEQUENCE.md`
   - For error handling patterns: `VPA_ERROR_HANDLING_STRATEGY.md`
   - For security considerations: `VPA_SECURITY_AND_PRIVACY_STRATEGY.md`

3. Look for architecture principles in `planning_docs/1_architecture/` documents

### Step 3: Create Document with Consistent Structure
1. Use consistent Markdown formatting (H1 for title, H2 for main sections)
2. Include standard sections based on document type:
   - For implementation phases: Overview, Timeline, Goals, Implementation Tasks, Testing
   - For component specs: Purpose, Architecture, APIs, Integration Points
   - For technical standards: Purpose, Standards, Examples, Validation

3. Include relevant code examples following established patterns
4. Add creation date at the bottom: `*Document created: August 29, 2025*`

### Step 4: Update MASTER_LOG.md
1. Update counts in "Completed Documents" section
2. Update counts in "Missing Documents" section
3. Add a new entry to the "Action Log" table
4. Update "Next Steps" section if applicable
5. Update the "Last updated" timestamp

## Key Technical Patterns to Maintain

### Architecture Consistency
- **Event-Driven Communication**: All components communicate via event bus
- **Async-First**: All I/O and long-running operations use asyncio patterns
- **Plugin Architecture**: Functionality extendable via plugin system
- **Performance Targets**: Startup <10s, memory <2GB, events <10ms, TTS <2s

### Code Pattern Consistency
- Event bus subscription/emission patterns
- Error handling with graceful degradation
- Plugin interface and discovery mechanisms
- Windows OS integration patterns

## Common Issues to Avoid

1. **Terminology Inconsistency** - Use consistent terms across all documents:
   - "Event Bus" not "Event System" or "Message Bus"
   - "Plugin Manager" not "Plugin System" or "Extension Manager"
   - "Application Manager" not "App Manager" or "Core Manager"

2. **Implementation Timeline Conflicts** - Ensure phase timelines align with:
   - `VPA_MASTER_IMPLEMENTATION_PLAN.md` for overall timeline
   - Previous phase documents for dependencies

3. **Technical Approach Divergence** - Maintain consistency with architectural decisions:
   - Async event-based communication
   - Plugin isolation and sandboxing
   - Performance-first approach

## Conclusion

Maintaining alignment is critical for creating a cohesive, implementable plan for the VPA project. By following this guide and consistently referencing the primary resources, we can ensure that all documentation is comprehensive, consistent, and provides clear guidance for the implementation phase.

---

*Document created: August 29, 2025*
