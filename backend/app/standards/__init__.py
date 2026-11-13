"""
Standards and compliance modules for AccessiAI.

This package contains references and implementations of accessibility standards:
- WCAG 2.2 (Web Content Accessibility Guidelines 2.2)
- Section 508 (US Federal accessibility requirements)

Reference: https://www.w3.org/TR/WCAG22/
"""

from app.standards.wcag22 import (
    DEFAULT_WCAG_STANDARDS,
    AXE_WCAG_TAGS,
    WCAG_2_2_AA_CRITERIA,
    WCAG_22_REFERENCE,
    WCAG_22_QUICK_REFERENCE,
    WCAG_22_UNDERSTANDING,
    WCAGLevel,
    WCAGPrinciple,
    WCAGVersion,
    PRIMARY_WCAG_LEVEL,
    PRIMARY_WCAG_VERSION,
    get_wcag_criteria_info,
    get_principles,
    filter_criteria_by_principle,
    filter_criteria_by_level,
)

__all__ = [
    "DEFAULT_WCAG_STANDARDS",
    "AXE_WCAG_TAGS",
    "WCAG_2_2_AA_CRITERIA",
    "WCAG_22_REFERENCE",
    "WCAG_22_QUICK_REFERENCE",
    "WCAG_22_UNDERSTANDING",
    "WCAGLevel",
    "WCAGPrinciple",
    "WCAGVersion",
    "PRIMARY_WCAG_LEVEL",
    "PRIMARY_WCAG_VERSION",
    "get_wcag_criteria_info",
    "get_principles",
    "filter_criteria_by_principle",
    "filter_criteria_by_level",
]
