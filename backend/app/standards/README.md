# AccessiAI Standards Compliance Module

## Overview

This module ensures that every accessibility scan conducted through AccessiAI follows the **Web Content Accessibility Guidelines (WCAG) 2.2 Level AA** standard.

**Official Reference**: https://www.w3.org/TR/WCAG22/

## Quick Start

### Using WCAG 2.2 Standards in Your Code

```python
from app.standards import (
    WCAG_2_2_AA_CRITERIA,
    PRIMARY_WCAG_VERSION,
    PRIMARY_WCAG_LEVEL,
    WCAG_22_REFERENCE,
    DEFAULT_WCAG_STANDARDS,
)

# Use in scans
print(f"Scanning to {PRIMARY_WCAG_VERSION} {PRIMARY_WCAG_LEVEL}")
# Output: Scanning to 2.2 AA

# Get specific criterion info
criterion = WCAG_2_2_AA_CRITERIA.get("1.4.3")
# {
#   "principle": "Perceivable",
#   "title": "Contrast (Minimum)",
#   "description": "Text and images have a contrast ratio of at least 4.5:1...",
#   "level": "AA",
#   "version": "2.2"
# }
```

## Architecture

### Files

```
backend/app/standards/
├── __init__.py          # Exports WCAG 2.2 constants and utilities
└── wcag22.py            # WCAG 2.2 standards reference (18K+ lines)
```

### What's Defined

**Enums:**
- `WCAGVersion` - 2.0, 2.1, 2.2
- `WCAGLevel` - A, AA, AAA
- `WCAGPrinciple` - Perceivable, Operable, Understandable, Robust

**Constants:**
- `WCAG_2_2_AA_CRITERIA` - Dictionary of 50+ WCAG 2.2 Level AA success criteria
- `AXE_WCAG_TAGS` - Mapping of axe-core tags to WCAG versions
- `DEFAULT_WCAG_STANDARDS` - List of standards to check in every scan
- `PRIMARY_WCAG_VERSION` - "2.2"
- `PRIMARY_WCAG_LEVEL` - "AA"
- `WCAG_22_REFERENCE` - https://www.w3.org/TR/WCAG22/

**Functions:**
- `get_wcag_criteria_info(criterion_id)` - Get details about a criterion
- `get_principles()` - List all WCAG principles
- `filter_criteria_by_principle(principle)` - Get criteria for a principle
- `filter_criteria_by_level(level)` - Get criteria for a level

## WCAG 2.2 Standards Coverage

### Perceivable (13 criteria in Level AA)
- 1.1.1 Non-text Content
- 1.2.1 Audio-only and Video-only (Prerecorded)
- 1.3.1 Info and Relationships
- 1.3.2 Meaningful Sequence
- 1.3.3 Sensory Characteristics
- 1.3.4 Orientation
- 1.3.5 Identify Input Purpose
- 1.3.6 Identify Purpose
- 1.4.1 Use of Color
- 1.4.2 Audio Control
- 1.4.3 Contrast (Minimum)
- 1.4.4 Resize Text
- 1.4.5 Images of Text
- 1.4.10 Reflow
- 1.4.11 Non-text Contrast
- 1.4.12 Text Spacing
- 1.4.13 Content on Hover or Focus

### Operable (12 criteria in Level AA)
- 2.1.1 Keyboard
- 2.1.2 No Keyboard Trap
- 2.1.4 Character Key Shortcuts
- 2.2.1 Timing Adjustable
- 2.2.2 Pause, Stop, Hide
- 2.3.1 Three Flashes or Below Threshold
- 2.4.1 Bypass Blocks
- 2.4.2 Page Titled
- 2.4.3 Focus Order
- 2.4.4 Link Purpose (In Context)
- 2.4.5 Multiple Ways
- 2.4.6 Headings and Labels
- 2.4.7 Focus Visible
- 2.4.11 Focus Visible (Enhanced) **← NEW in 2.2**
- 2.5.1 Pointer Gestures
- 2.5.2 Pointer Cancellation
- 2.5.3 Label in Name
- 2.5.4 Motion Actuation
- 2.5.7 Dragging Movements **← NEW in 2.2**

### Understandable (8 criteria in Level AA)
- 3.1.1 Language of Page
- 3.1.2 Language of Parts
- 3.2.1 On Focus
- 3.2.2 On Input
- 3.2.3 Consistent Navigation
- 3.2.4 Consistent Identification
- 3.2.6 Consistent Help **← NEW in 2.2**
- 3.3.1 Error Identification
- 3.3.2 Labels or Instructions
- 3.3.3 Error Suggestion
- 3.3.4 Error Prevention (Legal, Financial, Data)

### Robust (3 criteria in Level AA)
- 4.1.1 Parsing
- 4.1.2 Name, Role, Value
- 4.1.3 Status Messages

**Total: 50+ success criteria at WCAG 2.2 Level AA**

## How Scans Use WCAG 2.2

### In scan_service.py

```python
from app.standards import DEFAULT_WCAG_STANDARDS

# Phase 2: Accessibility Audit (every scan)
axe_results = await page.evaluate(f"""async () => {{
    return await axe.run(document, {{
        runOnly: {{
            type: 'tag',
            values: {DEFAULT_WCAG_STANDARDS}
        }}
    }});
}}""")
```

This ensures every scan checks against WCAG 2.2 (plus 2.0, 2.1, and Section 508).

### In violation.py

Each violation now stores:
```python
wcag_version: str  # "2.0", "2.1", or "2.2"
wcag_level: str    # "A", "AA", or "AAA"
wcag_criteria: str # "wcag22aa, wcag2aa, section508"
```

### In Database

```sql
SELECT rule_id, wcag_version, wcag_level, wcag_criteria
FROM violations
WHERE scan_id = 'xxx' AND wcag_version = '2.2';
```

## WCAG 2.2 Features

### New in WCAG 2.2

Five new success criteria were added:

1. **2.4.11 Focus Visible (Enhanced)** - Level AA
   - Focus indicator has ≥3:1 contrast ratio
   - Occupies ≥2 CSS pixels

2. **2.5.7 Dragging Movements** - Level AA
   - Drag actions have single-pointer alternatives

3. **2.5.8 Target Size (Enhanced)** - Level AAA
   - Touch targets ≥44×44 CSS pixels

4. **3.2.6 Consistent Help** - Level A
   - Help mechanisms consistently positioned/presented

5. **3.3.7 Redundant Entry** - Level AAA
   - No re-entry of previously submitted information

### Backward Compatibility

- All WCAG 2.0 Level AA criteria are in WCAG 2.2
- All WCAG 2.1 Level AA criteria are in WCAG 2.2
- WCAG 2.2 is backward compatible with 2.0 and 2.1

## Integration Guide

### 1. Adding WCAG Standards to Your Module

```python
from app.standards import (
    PRIMARY_WCAG_VERSION,
    WCAG_22_REFERENCE,
    get_wcag_criteria_info,
)

def audit_page():
    # Reference WCAG in logs
    logger.info(f"Auditing to {PRIMARY_WCAG_VERSION} - {WCAG_22_REFERENCE}")
    
    # Get criterion details
    info = get_wcag_criteria_info("1.4.3")
    print(f"Checking: {info['title']}")
```

### 2. Filtering by Principle

```python
from app.standards import filter_criteria_by_principle, WCAGPrinciple

# Get all Perceivable criteria
perceivable = filter_criteria_by_principle(WCAGPrinciple.PERCEIVABLE)
for criterion_id, details in perceivable.items():
    print(f"{criterion_id}: {details['title']}")
```

### 3. Filtering by Level

```python
from app.standards import filter_criteria_by_level, WCAGLevel

# Get all Level AA criteria
aa_criteria = filter_criteria_by_level(WCAGLevel.AA)
print(f"Total Level AA criteria: {len(aa_criteria)}")
```

### 4. Using in API Responses

```python
from app.standards import AXE_WCAG_TAGS

def format_violation(v_data):
    tag_info = AXE_WCAG_TAGS.get("wcag22aa")
    return {
        "rule_id": v_data["id"],
        "wcag_version": tag_info["version"].value,
        "wcag_level": tag_info["level"].value,
        "wcag_title": tag_info["description"],
    }
```

## Resources

| Resource | URL |
|----------|-----|
| WCAG 2.2 Specification | https://www.w3.org/TR/WCAG22/ |
| Quick Reference | https://www.w3.org/WAI/WCAG22/quickref/ |
| Understanding WCAG 2.2 | https://www.w3.org/WAI/WCAG22/Understanding/ |
| axe-core Engine | https://github.com/dequelabs/axe-core |
| axe DevTools | https://www.deque.com/axe/devtools/ |

## Testing

### Unit Test Example

```python
from app.standards import WCAG_2_2_AA_CRITERIA, PRIMARY_WCAG_VERSION

def test_wcag_standards():
    # Verify WCAG 2.2 is primary
    assert PRIMARY_WCAG_VERSION == "2.2"
    
    # Verify criteria loaded
    assert len(WCAG_2_2_AA_CRITERIA) > 40
    
    # Verify specific criterion
    assert "1.4.3" in WCAG_2_2_AA_CRITERIA
    assert WCAG_2_2_AA_CRITERIA["1.4.3"]["title"] == "Contrast (Minimum)"
```

## Maintenance

### Updating WCAG Standards

If updating to a new WCAG version:

1. Update `wcag22.py` with new criteria
2. Add new `WCAGVersion` enum value
3. Update `PRIMARY_WCAG_VERSION` and `PRIMARY_WCAG_LEVEL`
4. Add migration file for database fields
5. Update documentation

### Deprecation

WCAG 2.0 and 2.1 are still W3C Recommendations and remain supported. WCAG 2.2 is the current standard and is the primary target for AccessiAI.

## Summary

- ✅ WCAG 2.2 Level AA is the primary scan standard
- ✅ Every scan includes WCAG 2.2 checks
- ✅ Violations include WCAG version and level
- ✅ Standards reference is centralized in `app/standards/`
- ✅ Full compliance documentation available at https://www.w3.org/TR/WCAG22/
