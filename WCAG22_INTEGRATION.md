# WCAG 2.2 Integration

**Standard:** [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)

**Status:** W3C Recommendation (December 2023)

## How AccessiAI Enforces WCAG 2.2

Every scan runs [axe-core](https://github.com/dequelabs/axe-core) with the following rule tags enabled:

| Tag | Standard |
|-----|----------|
| `wcag2a` | WCAG 2.0 Level A |
| `wcag2aa` | WCAG 2.0 Level AA |
| `wcag21a` | WCAG 2.1 Level A |
| `wcag21aa` | WCAG 2.1 Level AA |
| `wcag22aa` | WCAG 2.2 Level AA |
| `section508` | US Section 508 |
| `best-practice` | Industry best practices |

WCAG 2.2 extends WCAG 2.1 and maintains backward compatibility with earlier versions. By including all tag levels, AccessiAI checks against the full WCAG 2.2 AA conformance target plus Section 508 compliance.

## WCAG 2.2 Principles (POUR)

1. **Perceivable** -- Content must be presentable in ways users can perceive
2. **Operable** -- UI must be navigable via keyboard, mouse, touch, and assistive tech
3. **Understandable** -- Content and behavior must be clear and predictable
4. **Robust** -- Content must work with current and future assistive technologies

## New in WCAG 2.2

- **2.4.11 Focus Not Obscured (Minimum)** -- Focused components are at least partially visible
- **2.4.12 Focus Not Obscured (Enhanced)** -- Focused components are fully visible (AAA)
- **2.4.13 Focus Appearance** -- Focus indicators meet minimum size and contrast (AAA)
- **2.5.7 Dragging Movements** -- Drag operations have single-pointer alternatives
- **2.5.8 Target Size (Minimum)** -- Interactive targets are at least 24x24 CSS pixels
- **3.2.6 Consistent Help** -- Help mechanisms are in a consistent location
- **3.3.7 Redundant Entry** -- Previously entered info is auto-populated or selectable
- **3.3.8 Accessible Authentication (Minimum)** -- No cognitive function test for auth
- **3.3.9 Accessible Authentication (Enhanced)** -- No object/content recognition test for auth (AAA)

## References

- WCAG 2.2 Specification: https://www.w3.org/TR/WCAG22/
- Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/
- Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/
- axe-core Rules: https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md
