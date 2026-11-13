import logging

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_analysis import AIAnalysis
from app.models.violation import Violation

logger = logging.getLogger(__name__)

MODEL_NAME = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are an expert web accessibility consultant. Given an accessibility violation detected by axe-core, provide a structured analysis with:

1. **Explanation**: A clear, developer-friendly explanation of what the violation means and why it matters.
2. **Applicable Standards**: Explain the WCAG success criteria and/or Section 508 provisions indicated by the supplied tags. Do not claim full compliance or legal conformance.
3. **Suggested Fix**: Provide a concrete HTML or React code fix that resolves the issue.
4. **User Impact**: Describe how this issue affects users with disabilities.
5. **Testing Recommendations**: Suggest how to verify the fix works.

Be concise but thorough. Format your response with clear markdown headings."""


async def analyze_violation(violation: Violation, db: AsyncSession, guidelines: str | None = None) -> AIAnalysis:
    elements_html = ""
    for el in violation.affected_elements:
        elements_html += f"- Selector: `{el.selector}`\n  HTML: `{el.html}`\n"
        if el.failure_summary:
            elements_html += f"  Failure: {el.failure_summary}\n"

    guidelines_section = ""
    if guidelines:
        guidelines_section = f"""

**Client Guidelines** (from uploaded attachments — apply these standards in your analysis):
{guidelines[:4000]}
"""

    user_message = f"""Analyze this accessibility violation:

**Rule ID**: {violation.rule_id}
**Description**: {violation.description}
**Impact**: {violation.impact}
**WCAG / Section 508 Tags**: {violation.wcag_criteria}
**Help URL**: {violation.help_url or 'N/A'}

**Affected Elements**:
{elements_html or 'No elements captured'}
{guidelines_section}"""

    if not settings.ANTHROPIC_API_KEY:
        analysis = AIAnalysis(
            violation_id=violation.id,
            explanation=f"**{violation.rule_id}**: {violation.description}\n\nThis is a {violation.impact}-level accessibility issue related to these standards tags: {violation.wcag_criteria}.",
            suggested_fix="AI analysis requires an Anthropic API key. Please configure ANTHROPIC_API_KEY to enable AI-powered suggestions.",
            model_name="fallback",
        )
        db.add(analysis)
        await db.flush()
        return analysis

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model=MODEL_NAME,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        content = response.content[0].text

        parts = content.split("## Suggested Fix", 1)
        explanation = parts[0].strip()
        suggested_fix = parts[1].strip() if len(parts) > 1 else content

        analysis = AIAnalysis(
            violation_id=violation.id,
            explanation=explanation,
            suggested_fix=suggested_fix,
            model_name=MODEL_NAME,
        )
        db.add(analysis)
        await db.flush()
        return analysis

    except Exception as e:
        logger.exception("AI analysis failed for violation %s: %s", violation.id, e)
        analysis = AIAnalysis(
            violation_id=violation.id,
            explanation=f"AI analysis encountered an error. Manual review recommended for: {violation.description}",
            suggested_fix=f"Please review the affected elements manually. Rule: {violation.rule_id}, Impact: {violation.impact}",
            model_name="error-fallback",
        )
        db.add(analysis)
        await db.flush()
        return analysis
