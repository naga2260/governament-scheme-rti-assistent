# RTI Generator Implementation Plan

## Overview

Build the RTI (Right to Information) draft generator that helps citizens create formal RTI requests to government departments.

## Implementation Strategy

### Phase 1: RTI Templates & Mapping
**Goal:** Create RTI format templates and department mappings

**Files to Create:**
- `utils/rti_generator.py` - RTI generation logic with templates

**Key Implementation:**
- Store RTI templates for different query types
- Create scheme-to-department mapping
- Support bilingual templates (English & Telugu)

### Phase 2: Draft Generation
**Goal:** Generate RTI drafts from user queries

**Files to Modify:**
- `utils/rti_generator.py` - Populate templates with user info
- Add RTI generation function

### Phase 3: UI Integration
**Goal:** Add RTI generation to Streamlit app

**Files to Modify:**
- `app.py` - Add RTI input and download functionality

### Phase 4: Testing & Refinement
**Goal:** Validate RTI format and department mappings

## References

See `spec.md` for full feature specification
