# Task Breakdown Template

Use this template to break down implementation work into specific, actionable tasks. Reference the `plan.md` for strategy and high-level approach.

## Metadata

- **Feature:** [Name]
- **Total Tasks:** [Number]
- **Status:** [Not Started | In Progress | Complete]
- **Owner:** [Developer]
- **Start Date:** [YYYY-MM-DD]
- **Target Completion:** [YYYY-MM-DD]

## Overview

[1-2 sentence summary: What are we building? What's the order of work?]

## Task Breakdown

### Phase 1: [Phase Name from plan.md]

#### Task 1.1: [Specific Task]
- **Description:** [What needs to be done]
- **Dependencies:** [Other tasks that must complete first]
- **Acceptance Criteria:**
  - [ ] Criterion 1 (testable)
  - [ ] Criterion 2 (observable)
- **Estimated Effort:** [X hours]
- **Files:** 
  - Create: `path/to/new_file.py`
  - Modify: `path/to/existing.py`
- **Related Code:** [Function name], [class name]
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

**Implementation Notes:**
```python
# Example code structure or pattern to follow
def task_implementation():
    pass
```

---

#### Task 1.2: [Another Task]
- **Description:** [What needs to be done]
- **Dependencies:** [Task 1.1]
- **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Estimated Effort:** [X hours]
- **Files:**
  - Create: []
  - Modify: []
- **Related Code:** []
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

**Testing:**
```python
# How to test this task
def test_task_1_2():
    # Expected behavior
    pass
```

---

#### Task 1.3: [Integration Task]
- **Description:** Connect components from Task 1.1 and 1.2
- **Dependencies:** [Task 1.1, Task 1.2]
- **Acceptance Criteria:**
  - [ ] Components integrated
  - [ ] No breaking changes to existing code
- **Estimated Effort:** [X hours]
- **Files:**
  - Modify: `app.py`, `utils/retriever.py`
- **Related Code:** []
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

---

### Phase 2: [Next Phase]

#### Task 2.1: [Task Name]
- **Description:** [...]
- **Dependencies:** [Phase 1 completion]
- **Acceptance Criteria:**
  - [ ] Criterion 1
- **Estimated Effort:** [X hours]
- **Files:** []
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

---

### Phase 3: Testing & Deployment

#### Task 3.1: Comprehensive Testing
- **Description:** Run full test suite, manual testing, edge cases
- **Dependencies:** [All phase 1 & 2 tasks complete]
- **Acceptance Criteria:**
  - [ ] Unit tests: 100% pass
  - [ ] Integration tests pass
  - [ ] Manual testing checklist complete (see plan.md)
  - [ ] No linting/type errors: `ruff check .` & `mypy app.py utils`
- **Estimated Effort:** [X hours]
- **Testing Checklist:**
  - [ ] Run pytest locally
  - [ ] Run pre-commit hooks
  - [ ] Test in Streamlit UI
  - [ ] Verify Telugu translations
  - [ ] Performance acceptable
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

---

#### Task 3.2: Documentation
- **Description:** Update README, CONTRIBUTING, or create spec files
- **Dependencies:** Feature implementation complete
- **Acceptance Criteria:**
  - [ ] README updated with new feature
  - [ ] API docs accurate
  - [ ] Examples provided
  - [ ] Comments added where needed
- **Estimated Effort:** [X hours]
- **Files:**
  - Modify: `README.md`, `CONTRIBUTING.md`
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

---

#### Task 3.3: Code Review Prep & Merge
- **Description:** Clean up commits, squash if needed, prepare for review
- **Dependencies:** [Documentation task complete]
- **Acceptance Criteria:**
  - [ ] Commits squashed to logical units
  - [ ] Commit messages clear and descriptive
  - [ ] PR created with context and testing notes
  - [ ] All CI checks pass
  - [ ] Code review feedback addressed
  - [ ] Ready to merge to main
- **Estimated Effort:** [X hours]
- **Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

---

## Progress Tracking

### Summary
| Phase | Tasks | Complete | Remaining | % Done |
|-------|-------|----------|-----------|--------|
| Phase 1 | 3 | 0 | 3 | 0% |
| Phase 2 | 1 | 0 | 1 | 0% |
| Phase 3 | 3 | 0 | 3 | 0% |
| **Total** | **7** | **0** | **7** | **0%** |

### Current Focus
- **Next Task:** [Task 1.1]
- **Last Updated:** [Timestamp]
- **Blockers:** None

## Key Dates

- **Start:** [YYYY-MM-DD]
- **Phase 1 Target:** [YYYY-MM-DD]
- **Phase 2 Target:** [YYYY-MM-DD]
- **Final Completion:** [YYYY-MM-DD]

## Communication Plan

- **Daily Standup:** [Time/frequency]
- **Code Review:** [How often]
- **Testing Feedback:** [Who tests, when]
- **Blockers:** [How to escalate]

## Rollback & Contingency

- **If Phase 1 fails:** [Contingency plan]
- **If testing fails:** [Revert to last stable, debug]
- **If deadline at risk:** [Scope reduction plan]

## Lessons Learned (Post-Implementation)

[Fill this in after tasks complete]

- **What went well:** [Successes]
- **What was challenging:** [Difficulties]
- **Next time:** [Improvements]
- **Documentation needed:** [What helped/hindered]

## References

- [Spec](spec.md) - Feature specification & acceptance criteria
- [Plan](plan.md) - Implementation strategy
- [Constitution](../../.specify/memory/constitution.md) - Project standards
- [GitHub Issue/PR]

---

**Last Updated:** [YYYY-MM-DD HH:MM UTC]
