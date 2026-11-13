"""
WCAG 2.2 Standards Reference
Reference: https://www.w3.org/TR/WCAG22/

This module defines and enforces Web Content Accessibility Guidelines (WCAG) 2.2
compliance across all accessibility scans.

WCAG 2.2 is a W3C Recommendation published December 12, 2024, and is the current
standard for web accessibility. It extends WCAG 2.1 and maintains backward compatibility
with WCAG 2.0 and 2.1.

Four Principles (POUR):
- Perceivable: Information must be presentable to users in ways they can perceive
- Operable: Functionality must be usable via keyboard, mouse, touch, or assistive tech
- Understandable: Content and interface behavior must be clear and comprehensible
- Robust: Content must be compatible with current and future assistive technologies
"""

from enum import Enum
from typing import List


class WCAGPrinciple(str, Enum):
    """WCAG 2.2 Four Principles (POUR)"""
    PERCEIVABLE = "Perceivable"
    OPERABLE = "Operable"
    UNDERSTANDABLE = "Understandable"
    ROBUST = "Robust"


class WCAGLevel(str, Enum):
    """WCAG Conformance Levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class WCAGVersion(str, Enum):
    """WCAG Versions"""
    WCAG_2_0 = "2.0"
    WCAG_2_1 = "2.1"
    WCAG_2_2 = "2.2"


# WCAG 2.2 Level AA Success Criteria (Primary target for AccessiAI)
# Reference: https://www.w3.org/WAI/WCAG22/quickref/
WCAG_2_2_AA_CRITERIA = {
    # Perceivable Principle
    "1.1.1": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Non-text Content",
        "description": "All non-text content has a text alternative that serves the equivalent purpose",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.2.1": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Audio-only and Video-only (Prerecorded)",
        "description": "Provide alternatives for prerecorded audio-only and video-only media",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.1": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Info and Relationships",
        "description": "Information, structure, and relationships conveyed through presentation are preserved",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.2": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Meaningful Sequence",
        "description": "The order of content follows a meaningful sequence",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.3": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Sensory Characteristics",
        "description": "Instructions do not rely solely on shape, size, visual location, orientation, or sound",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.4": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Orientation",
        "description": "Content is not restricted to a single orientation (portrait or landscape)",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.5": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Identify Input Purpose",
        "description": "The purpose of each input field can be programmatically determined",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.3.6": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Identify Purpose",
        "description": "The purpose of buttons, links, and other user interface components can be identified",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.1": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Use of Color",
        "description": "Color is not used as the only means of conveying information",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.2": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Audio Control",
        "description": "If audio plays automatically for more than 3 seconds, it can be paused or muted",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.3": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Contrast (Minimum)",
        "description": "Text and images have a contrast ratio of at least 4.5:1 (3:1 for large text)",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.4": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Resize Text",
        "description": "Except for captions and images of text, text can be resized up to 200% without loss of function",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.5": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Images of Text",
        "description": "Text is used instead of images of text, unless unavoidable",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.10": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Reflow",
        "description": "Content can be presented without loss of information or functionality at 320 CSS pixels width",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.11": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Non-text Contrast",
        "description": "Icons and graphics have a contrast ratio of at least 3:1 against adjacent colors",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.12": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Text Spacing",
        "description": "Content remains accessible when users adjust text spacing (line height, letter spacing, etc.)",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "1.4.13": {
        "principle": WCAGPrinciple.PERCEIVABLE,
        "title": "Content on Hover or Focus",
        "description": "Hover or focus-triggered content can be dismissed and remains visible on hover",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    # Operable Principle
    "2.1.1": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Keyboard",
        "description": "All functionality is operable via keyboard interface",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.1.2": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "No Keyboard Trap",
        "description": "Keyboard focus can move away from any component using only keyboard",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.1.4": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Character Key Shortcuts",
        "description": "If keyboard shortcuts use only character keys, users can disable or remap them",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.2.1": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Timing Adjustable",
        "description": "Users can extend time limits or disable them",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.2.2": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Pause, Stop, Hide",
        "description": "Moving, blinking, or scrolling content can be paused or stopped",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.3.1": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Three Flashes or Below Threshold",
        "description": "No content flashes more than 3 times per second",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.1": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Bypass Blocks",
        "description": "A mechanism is provided to bypass repeated blocks of content",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.2": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Page Titled",
        "description": "Web pages have descriptive titles that identify their purpose",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.3": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Focus Order",
        "description": "Elements receive focus in a logical order",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.4": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Link Purpose (In Context)",
        "description": "The purpose of each link is clear from link text or context",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.5": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Multiple Ways",
        "description": "Multiple ways to locate a page within a set of pages are available",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.6": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Headings and Labels",
        "description": "Headings and labels describe the topic or purpose",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.7": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Focus Visible",
        "description": "Any component that receives keyboard focus has a visible focus indicator",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.4.11": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Focus Visible (Enhanced)",
        "description": "Focus indicator has a minimum 3:1 contrast ratio and occupies at least 2 CSS pixels",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
        "note": "NEW in WCAG 2.2",
    },
    "2.5.1": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Pointer Gestures",
        "description": "Single-pointer gestures can be performed with a single tap or click",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.5.2": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Pointer Cancellation",
        "description": "Functions triggered by pointer down events can be aborted",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.5.3": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Label in Name",
        "description": "For UI components with a visible text label, the accessible name includes the label",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.5.4": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Motion Actuation",
        "description": "Functions actuated by device motion can be performed via keyboard",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "2.5.7": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Dragging Movements",
        "description": "Functions that can be performed by dragging can also be performed with single-pointer click/tap",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
        "note": "NEW in WCAG 2.2",
    },
    "2.5.8": {
        "principle": WCAGPrinciple.OPERABLE,
        "title": "Target Size (Enhanced)",
        "description": "Touch targets and user interface components are at least 44x44 CSS pixels",
        "level": WCAGLevel.AAA,
        "version": WCAGVersion.WCAG_2_2,
    },
    # Understandable Principle
    "3.1.1": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Language of Page",
        "description": "The default language of the page is identified",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.1.2": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Language of Parts",
        "description": "The language of each passage or phrase is identified",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.2.1": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "On Focus",
        "description": "No unexpected context change occurs when receiving focus",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.2.2": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "On Input",
        "description": "No unexpected context change occurs when receiving input",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.2.3": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Consistent Navigation",
        "description": "Navigation mechanisms are consistent across pages",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.2.4": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Consistent Identification",
        "description": "UI components that serve the same function are consistently identified",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.2.6": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Consistent Help",
        "description": "Help and support mechanisms are consistently placed and presented",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
        "note": "NEW in WCAG 2.2",
    },
    "3.3.1": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Error Identification",
        "description": "Errors are identified and described in plain language",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.3.2": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Labels or Instructions",
        "description": "Labels or instructions are provided for user input",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.3.3": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Error Suggestion",
        "description": "Error correction suggestions are provided",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    "3.3.4": {
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "title": "Error Prevention (Legal, Financial, Data)",
        "description": "Transactions and deletions can be reversed or confirmed",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
    # Robust Principle
    "4.1.1": {
        "principle": WCAGPrinciple.ROBUST,
        "title": "Parsing",
        "description": "Web pages are free of parsing errors in HTML",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "4.1.2": {
        "principle": WCAGPrinciple.ROBUST,
        "title": "Name, Role, Value",
        "description": "For all user interface components, name, role, state, and value are available to assistive technologies",
        "level": WCAGLevel.A,
        "version": WCAGVersion.WCAG_2_2,
    },
    "4.1.3": {
        "principle": WCAGPrinciple.ROBUST,
        "title": "Status Messages",
        "description": "Status messages are announced to assistive technologies without focus",
        "level": WCAGLevel.AA,
        "version": WCAGVersion.WCAG_2_2,
    },
}

# AXE-CORE TAGS MAPPING
# Maps axe-core tags to WCAG versions and levels
AXE_WCAG_TAGS = {
    "wcag2a": {
        "version": WCAGVersion.WCAG_2_0,
        "level": WCAGLevel.A,
        "description": "Web Content Accessibility Guidelines 2.0 Level A",
    },
    "wcag2aa": {
        "version": WCAGVersion.WCAG_2_0,
        "level": WCAGLevel.AA,
        "description": "Web Content Accessibility Guidelines 2.0 Level AA",
    },
    "wcag21a": {
        "version": WCAGVersion.WCAG_2_1,
        "level": WCAGLevel.A,
        "description": "Web Content Accessibility Guidelines 2.1 Level A",
    },
    "wcag21aa": {
        "version": WCAGVersion.WCAG_2_1,
        "level": WCAGLevel.AA,
        "description": "Web Content Accessibility Guidelines 2.1 Level AA",
    },
    "wcag22aa": {
        "version": WCAGVersion.WCAG_2_2,
        "level": WCAGLevel.AA,
        "description": "Web Content Accessibility Guidelines 2.2 Level AA",
    },
    "wcag22aaa": {
        "version": WCAGVersion.WCAG_2_2,
        "level": WCAGLevel.AAA,
        "description": "Web Content Accessibility Guidelines 2.2 Level AAA",
    },
    "section508": {
        "version": WCAGVersion.WCAG_2_2,
        "level": WCAGLevel.AA,
        "description": "US Section 508 Compliance (based on WCAG)",
    },
}

# DEFAULT WCAG STANDARDS FOR ACCESSIBILITY SCANS
# Reference: https://www.w3.org/TR/WCAG22/
DEFAULT_WCAG_STANDARDS = [
    "wcag2a",      # WCAG 2.0 Level A (baseline)
    "wcag2aa",     # WCAG 2.0 Level AA (standard)
    "wcag21a",     # WCAG 2.1 Level A (updated)
    "wcag21aa",    # WCAG 2.1 Level AA (updated)
    "wcag22aa",    # WCAG 2.2 Level AA (CURRENT - W3C Recommendation Dec 2024)
    "section508",  # US Federal compliance
    "best-practice",  # Industry best practices
]

# PRIMARY WCAG VERSION AND LEVEL TARGET
PRIMARY_WCAG_VERSION = WCAGVersion.WCAG_2_2
PRIMARY_WCAG_LEVEL = WCAGLevel.AA

# WCAG 2.2 References
WCAG_22_REFERENCE = "https://www.w3.org/TR/WCAG22/"
WCAG_22_QUICK_REFERENCE = "https://www.w3.org/WAI/WCAG22/quickref/"
WCAG_22_UNDERSTANDING = "https://www.w3.org/WAI/WCAG22/Understanding/"


def get_wcag_criteria_info(criterion_id: str) -> dict:
    """Get detailed information about a specific WCAG criterion."""
    return WCAG_2_2_AA_CRITERIA.get(criterion_id, {})


def get_principles() -> List[WCAGPrinciple]:
    """Get all WCAG principles."""
    return [p for p in WCAGPrinciple]


def filter_criteria_by_principle(principle: WCAGPrinciple) -> dict:
    """Get all criteria for a specific principle."""
    return {
        criterion_id: details
        for criterion_id, details in WCAG_2_2_AA_CRITERIA.items()
        if details["principle"] == principle
    }


def filter_criteria_by_level(level: WCAGLevel) -> dict:
    """Get all criteria for a specific conformance level."""
    return {
        criterion_id: details
        for criterion_id, details in WCAG_2_2_AA_CRITERIA.items()
        if details["level"] == level
    }
