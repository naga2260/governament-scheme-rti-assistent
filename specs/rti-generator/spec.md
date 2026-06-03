# RTI (Right to Information) Generator Feature Specification

## Metadata

- **Title:** RTI Draft Generator
- **Status:** Complete
- **Owner:** Development Team
- **Created:** 2024-06-03
- **Target Release:** v0.1.0

## Overview

The RTI Generator helps citizens draft Right to Information requests (RTI applications) to be submitted to government departments. Given a user's query about a welfare scheme or government service, the system generates a formal RTI request with:
- Proper RTI format and legal language
- Identification of the correct department/public authority
- Relevant questions about scheme implementation, eligibility criteria, application status
- Links to submission procedures

Users can customize the draft and submit to appropriate authorities. This feature operates in English and Telugu.

## Acceptance Criteria

- [x] Generate formal RTI drafts with correct format
- [x] Map queries to correct government departments
- [x] Include scheme-specific questions in RTI
- [x] Bilingual support (English/Telugu)
- [x] User can download/edit RTI draft
- [x] RTI submission guidance provided

## Scope

### In Scope
- Generate RTI requests based on user queries about schemes
- Department mapping (which query → which department)
- Legal RTI format and language
- Downloadable RTI document (.txt or .pdf)
- Guidance on RTI submission process

### Out of Scope
- Actual submission to government departments (out of scope, user responsibility)
- Tracking RTI responses or follow-ups
- Legal representation or advice
- Handling of sensitive/confidential information

## Design & Architecture

### High-Level Design

```
User Query (about scheme/service)
    ↓
Query Analysis (identify scheme/issue)
    ↓
Department Mapping (query → public authority)
    ↓
RTI Template Selection (based on query type)
    ↓
Populate RTI with:
  - Applicant info fields (to be filled by user)
  - Department details
  - Specific questions
  - Reference scheme/section info
    ↓
Format as Legal Document (proper RTI format)
    ↓
Offer Download/Edit Options (TXT or PDF)
    ↓
Provide Submission Guidance (where to submit, format, fees)
    ↓
Streamlit UI Display
```

### Key Components

- **RTI Generator (`utils/rti_generator.py`):** Core logic for RTI draft creation
- **Department Mapper:** Lookup table (query topic → department authority)
- **Template Engine:** RTI format templates for different query types
- **Document Export:** Convert RTI to downloadable format (TXT, markdown)
- **UI Component (`app.py`):** Streamlit form for RTI generation

### API & Integration Points

```python
# Core RTI generator interface
def generate_rti_draft(
    query: str,
    user_profile: dict,
    lang: str = 'en'
) -> RTIDraft:
    """Generate RTI draft with user info and query details."""

def get_department_for_scheme(scheme_name: str) -> Department:
    """Map scheme name to responsible government department."""
```

## Implementation Details

### Technology Choices

1. **Template-Based Generation:**
   - Chosen for: Simple, maintainable, no complex NLP needed
   - Approach: Pre-built RTI templates with placeholders for scheme/department names
   
2. **Department Mapping:**
   - Chosen for: Simple lookup, easily maintainable
   - Approach: Hardcoded mapping or CSV-based lookup of schemes → departments

3. **Document Format:**
   - Chosen for: TXT (simple), Markdown (readable), PDF (optional future)
   - Current: Plain text format with clear structure

### RTI Format Standards

RTI applications follow this structure:
```
To: [Department/Authority Name]
[Address]

RTI Application under Section 6 of RTI Act, 2005

Dear Sir/Madam,

I, [Applicant Name], hereby submit this application for information...

[Specific Questions]

[Reference Information]

[Attachments list]

Sincerely,
[Applicant Signature]
```

### Multilingual Support

- **Language Selection:** User selects English or Telugu
- **Template Translations:** RTI templates translated to Telugu
- **Output Language:** RTI draft generated in selected language
- **Department Names:** Translated to match language selection

### Testing Strategy

- **Unit Tests:** Test department mapping, template population
- **Integration Tests:** End-to-end query → RTI draft
- **Manual Testing:** Generate RTI for sample schemes, verify accuracy
- **Format Testing:** Verify RTI format matches official standards

## Multilingual Support
- [x] English RTI templates finalized
- [x] Telugu RTI templates available
- [x] Language selector tested

## Dependencies & Risks

### External Dependencies
- None (self-contained logic)

### Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incorrect department identified | Medium | Manual review of mappings, community feedback |
| RTI format doesn't match standards | Medium | Reference official RTI guidelines, test with experts |
| Missing scheme mappings | Low | Expandable mapping as schemes added |
| Language translation quality | Low | Professional review of Telugu translations |

### Performance Impact

- **Latency:** RTI generation < 500ms (pure template work)
- **Memory:** Minimal (small templates and mappings)
- **Storage:** Mappings file ~50KB

## Acceptance & Validation

### Definition of Done
- [x] RTI drafts generate in correct format
- [x] Department mapping 95%+ accurate
- [x] Telugu RTI templates complete
- [x] Download functionality works
- [x] No sensitive data exposed
- [x] Unit and integration tests pass
- [x] Code review approved

### Validation Steps
1. Generate RTI for "MGNERGA" scheme → Verify Rural Development dept identified
2. Generate RTI (Telugu) → Verify Telugu format and translations
3. Download RTI → Verify TXT file readable and properly formatted
4. Test with multiple schemes → Verify no missing department mappings

## Timeline & Effort

- **Estimated Effort:** 20 hours
- **Implementation Plan:** See `plan.md`
- **Task Breakdown:** See `tasks.md`
- **Status:** ✅ Complete

## Known Issues & Limitations

- **Limitation 1:** Department mappings are scheme-specific — additional schemes may have unmapped departments
- **Limitation 2:** RTI format assumes basic Indian RTI rules — may need customization for specific states
- **Limitation 3:** Does not provide legal advice on RTI filing strategy

## References

- [Plan](plan.md) - Implementation strategy
- [Tasks](tasks.md) - Task breakdown
- [Constitution](../../.specify/memory/constitution.md) - Project standards
- RTI Act 2005: https://www.dopt.gov.in/rti-act
- Official RTI Template Resources

---

**Status:** ✅ Feature Complete
**Last Updated:** 2024-06-03
