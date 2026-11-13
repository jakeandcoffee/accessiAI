import asyncio
import html
import ipaddress
import logging
import re
import socket
from collections import deque
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from uuid import UUID

from app.core.config import settings
from app.database.connection import async_session
from app.models.affected_element import AffectedElement
from app.models.scan import Scan
from app.models.violation import Violation
from app.services.scan_progress import emit

logger = logging.getLogger(__name__)

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

AXE_CORE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: no hostname")
    try:
        resolved = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise ValueError(f"DNS resolution failed for {hostname}") from e
    for family, _, _, _, addr in resolved:
        ip = ipaddress.ip_address(addr[0])
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError(f"Access to {hostname} is blocked (private/reserved IP)")
    return url


async def _audit_page(page, scan_id: str, check_site_files: bool) -> dict:
    """Run all six audit phases against an already-loaded page."""
    all_violations = []

    # ── Phase 1: Data Quality & Measurement ──
    emit(scan_id, "Phase 1: Data Quality & Measurement", "Checking analytics and tracking setup", phase="Phase 1: Data Quality")

    phase1_results = await page.evaluate("""() => {
        const findings = [];

        // Check for GTM
        const hasGTM = !!document.querySelector('script[src*="googletagmanager"]') ||
                       !!window.google_tag_manager || !!window.dataLayer;

        // Check for GA4
        const hasGA4 = !!document.querySelector('script[src*="gtag/js"]') ||
                       (typeof window.gtag === 'function');

        if (!hasGTM && !hasGA4) {
            findings.push({
                rule_id: 'data-quality/no-analytics',
                description: 'No Google Tag Manager or GA4 detected on the page',
                impact: 'critical',
                detail: 'Analytics tracking is essential for measuring user behavior and site performance'
            });
        }

        // Check for dataLayer
        if (!window.dataLayer) {
            findings.push({
                rule_id: 'data-quality/no-datalayer',
                description: 'No dataLayer object found — event tracking may not be configured',
                impact: 'serious',
                detail: 'dataLayer is required for proper GTM event tracking'
            });
        }

        // Check for duplicate script tags
        const scripts = Array.from(document.querySelectorAll('script[src]'));
        const srcCounts = {};
        scripts.forEach(s => {
            const src = s.getAttribute('src');
            srcCounts[src] = (srcCounts[src] || 0) + 1;
        });
        Object.entries(srcCounts).forEach(([src, count]) => {
            if (count > 1 && (src.includes('gtag') || src.includes('analytics') || src.includes('gtm'))) {
                findings.push({
                    rule_id: 'data-quality/duplicate-tracking',
                    description: `Duplicate tracking script detected: loaded ${count} times`,
                    impact: 'serious',
                    detail: `Script: ${src}`
                });
            }
        });

        // Check for UTM parameter handling
        const links = Array.from(document.querySelectorAll('a[href*="utm_"]'));
        const utmMedians = new Set();
        links.forEach(a => {
            const url = new URL(a.href, window.location.origin);
            const medium = url.searchParams.get('utm_medium');
            if (medium) utmMedians.add(medium.toLowerCase());
        });
        if (utmMedians.size > 3) {
            findings.push({
                rule_id: 'data-quality/inconsistent-utm',
                description: `${utmMedians.size} different utm_medium values found — consider standardizing`,
                impact: 'moderate',
                detail: `Values: ${Array.from(utmMedians).join(', ')}`
            });
        }

        // Check for form tracking
        const forms = document.querySelectorAll('form');
        if (forms.length > 0) {
            const hasFormTracking = !!document.querySelector('[data-gtm-form]') ||
                                   !!document.querySelector('[data-analytics]') ||
                                   (window.dataLayer && JSON.stringify(window.dataLayer).includes('form'));
            if (!hasFormTracking) {
                findings.push({
                    rule_id: 'data-quality/untracked-forms',
                    description: `${forms.length} form(s) found without detectable event tracking`,
                    impact: 'serious',
                    detail: 'Forms should fire form_start and form_submit events'
                });
            }
        }

        // Check for site search tracking
        const hasSearch = !!document.querySelector('input[type="search"]') ||
                         !!document.querySelector('[role="search"]') ||
                         !!document.querySelector('form[action*="search"]');
        if (hasSearch) {
            findings.push({
                rule_id: 'data-quality/search-tracking',
                description: 'Site search detected — verify view_search_results event is implemented',
                impact: 'moderate',
                detail: 'Search behavior tracking helps understand user intent'
            });
        }

        return findings;
    }""")

    for f in phase1_results:
        emit(scan_id, f"Found: {f['rule_id']}", f['description'], phase="Phase 1: Data Quality")

    all_violations.extend([{**f, "category": "data-quality"} for f in phase1_results])
    emit(scan_id, f"Phase 1 complete", f"{len(phase1_results)} issues found", phase="Phase 1: Data Quality")

    # ── Phase 2: Accessibility Audit (WCAG 2.2 AA and Section 508) ──
    emit(scan_id, "Phase 2: Accessibility Audit", "Injecting axe-core engine", phase="Phase 2: Accessibility")

    await page.evaluate("""async () => {
        const script = document.createElement('script');
        script.src = '%s';
        document.head.appendChild(script);
        await new Promise((resolve, reject) => {
            script.onload = resolve;
            script.onerror = reject;
        });
    }""" % AXE_CORE_CDN)

    emit(scan_id, "Running WCAG 2.2 AA and Section 508 audit", "Analyzing applicable accessibility rules", phase="Phase 2: Accessibility")

    axe_results = await page.evaluate("""async () => {
        return await axe.run(document, {
            runOnly: {
                type: 'tag',
                values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'section508', 'best-practice']
            }
        });
    }""")

    axe_violations = axe_results.get("violations", [])
    axe_passes = len(axe_results.get("passes", []))

    for v in axe_violations:
        emit(scan_id, f"Found: {v.get('id')}", v.get('description', ''), phase="Phase 2: Accessibility")

    emit(scan_id, f"Phase 2 complete", f"{len(axe_violations)} violations, {axe_passes} rules passed", phase="Phase 2: Accessibility")

    # ── Phase 3: GEO Audit (Generative Engine Optimization) ──
    emit(scan_id, "Phase 3: GEO Audit", "Checking AI/search engine readability", phase="Phase 3: GEO")

    phase3_results = await page.evaluate("""() => {
        const findings = [];

        // Check for JSON-LD schema markup
        const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
        if (jsonLdScripts.length === 0) {
            findings.push({
                rule_id: 'geo/no-schema-markup',
                description: 'No JSON-LD structured data found — add Organization, WebPage, FAQPage, BreadcrumbList schemas',
                impact: 'critical',
                detail: 'Structured data helps AI engines and search engines understand page content'
            });
        } else {
            const types = [];
            jsonLdScripts.forEach(s => {
                try { const d = JSON.parse(s.textContent); types.push(d['@type'] || 'unknown'); } catch {}
            });
            const needed = ['Organization', 'WebPage', 'FAQPage', 'BreadcrumbList'];
            const missing = needed.filter(t => !types.some(tt => tt.includes(t)));
            if (missing.length > 0) {
                findings.push({
                    rule_id: 'geo/incomplete-schema',
                    description: `Missing schema types: ${missing.join(', ')}`,
                    impact: 'serious',
                    detail: `Found types: ${types.join(', ')}`
                });
            }
        }

        // Check for publication/modification dates
        const hasDateMeta = !!document.querySelector('meta[property="article:published_time"]') ||
                            !!document.querySelector('meta[name="date"]') ||
                            !!document.querySelector('time[datetime]');
        if (!hasDateMeta) {
            findings.push({
                rule_id: 'geo/no-content-dates',
                description: 'No publication or modification dates found on the page',
                impact: 'serious',
                detail: 'Dates signal content freshness to AI engines and search crawlers'
            });
        }

        // Check for FAQ sections
        const hasFAQ = !!document.querySelector('[itemtype*="FAQPage"]') ||
                       document.body.innerText.toLowerCase().includes('frequently asked') ||
                       !!document.querySelector('details') ||
                       !!document.querySelector('[data-faq]');
        if (!hasFAQ) {
            findings.push({
                rule_id: 'geo/no-faq-section',
                description: 'No FAQ section detected — add contextual Q&A content for AI discoverability',
                impact: 'moderate',
                detail: 'FAQ sections in question format improve AI citation likelihood'
            });
        }

        // Check heading format (question-style)
        const headings = Array.from(document.querySelectorAll('h2, h3'));
        const questionHeadings = headings.filter(h => h.textContent.trim().endsWith('?'));
        if (headings.length > 3 && questionHeadings.length === 0) {
            findings.push({
                rule_id: 'geo/no-question-headings',
                description: 'No headings use question format — rewrite applicable headings as questions for better GEO',
                impact: 'moderate',
                detail: `${headings.length} headings found, none in question format`
            });
        }

        // Check for summary/TL;DR at top
        const firstP = document.querySelector('main p, article p, .content p, body > div p');
        const hasSummary = !!document.querySelector('[class*="summary"]') ||
                           !!document.querySelector('[class*="tldr"]') ||
                           !!document.querySelector('[class*="overview"]');
        if (!hasSummary && firstP) {
            findings.push({
                rule_id: 'geo/no-page-summary',
                description: 'No page summary or TL;DR section detected at top of content',
                impact: 'moderate',
                detail: 'A bulleted summary helps AI engines extract key information'
            });
        }

        // Check for external credibility links
        const links = Array.from(document.querySelectorAll('a[href]'));
        const credibleDomains = ['fda.gov', 'nih.gov', 'cms.gov', 'cdc.gov', 'who.int', 'pubmed'];
        const hasCredibleLinks = links.some(a => credibleDomains.some(d => a.href.includes(d)));
        if (!hasCredibleLinks) {
            findings.push({
                rule_id: 'geo/no-credibility-links',
                description: 'No links to authoritative sources (FDA, NIH, CMS) found',
                impact: 'serious',
                detail: 'External credibility links signal trustworthiness to AI engines'
            });
        }

        // Check for internal cross-linking
        const internalLinks = links.filter(a => a.hostname === window.location.hostname && !a.href.includes('#'));
        if (internalLinks.length < 3) {
            findings.push({
                rule_id: 'geo/weak-internal-linking',
                description: `Only ${internalLinks.length} internal links found — improve cross-linking between pages`,
                impact: 'moderate',
                detail: 'Strong internal linking helps both search engines and AI crawlers navigate content'
            });
        }

        // Check alt text quality
        const images = Array.from(document.querySelectorAll('img'));
        let poorAlt = 0;
        images.forEach(img => {
            const alt = img.getAttribute('alt');
            if (alt && (alt === img.src || alt.length < 5 || /^img|image|photo|picture$/i.test(alt))) {
                poorAlt++;
            }
        });
        if (poorAlt > 0) {
            findings.push({
                rule_id: 'geo/poor-alt-text',
                description: `${poorAlt} image(s) have non-descriptive alt text`,
                impact: 'serious',
                detail: 'Alt text should meaningfully describe the image content'
            });
        }

        return findings;
    }""")

    for f in phase3_results:
        emit(scan_id, f"Found: {f['rule_id']}", f['description'], phase="Phase 3: GEO")

    all_violations.extend([{**f, "category": "geo"} for f in phase3_results])
    emit(scan_id, f"Phase 3 complete", f"{len(phase3_results)} issues found", phase="Phase 3: GEO")

    # ── Phase 4: UX & Performance ──
    emit(scan_id, "Phase 4: UX & Performance", "Analyzing page performance and usability", phase="Phase 4: UX & Performance")

    phase4_results = await page.evaluate("""() => {
        const findings = [];

        // Check image optimization
        const images = Array.from(document.querySelectorAll('img'));
        let unoptimized = 0;
        let noLazy = 0;
        let noSrcset = 0;
        images.forEach(img => {
            const src = img.src || '';
            if (!src.includes('.webp') && !src.includes('.avif') && !src.includes('data:') && !src.includes('.svg')) {
                unoptimized++;
            }
            if (!img.loading || img.loading !== 'lazy') {
                const rect = img.getBoundingClientRect();
                if (rect.top > window.innerHeight) noLazy++;
            }
            if (!img.srcset && !img.closest('picture')) {
                noSrcset++;
            }
        });
        if (unoptimized > 0) {
            findings.push({
                rule_id: 'ux/unoptimized-images',
                description: `${unoptimized} of ${images.length} images not in modern format (WebP/AVIF)`,
                impact: 'serious',
                detail: 'Convert images to WebP or AVIF for faster loading'
            });
        }
        if (noLazy > 0) {
            findings.push({
                rule_id: 'ux/no-lazy-loading',
                description: `${noLazy} below-fold images missing lazy loading attribute`,
                impact: 'moderate',
                detail: 'Add loading="lazy" to images below the fold'
            });
        }
        if (noSrcset > 2) {
            findings.push({
                rule_id: 'ux/no-responsive-images',
                description: `${noSrcset} images without srcset — not responsive`,
                impact: 'moderate',
                detail: 'Use srcset for responsive image loading across device sizes'
            });
        }

        // Check viewport meta
        const viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            findings.push({
                rule_id: 'ux/no-viewport-meta',
                description: 'No viewport meta tag — page may not be mobile responsive',
                impact: 'critical',
                detail: 'Add <meta name="viewport" content="width=device-width, initial-scale=1">'
            });
        }

        // Check touch target sizes
        const clickables = Array.from(document.querySelectorAll('a, button, input, select, textarea'));
        let smallTargets = 0;
        clickables.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0 && (rect.width < 44 || rect.height < 44)) {
                smallTargets++;
            }
        });
        if (smallTargets > 3) {
            findings.push({
                rule_id: 'ux/small-touch-targets',
                description: `${smallTargets} interactive elements smaller than 44x44px minimum touch target`,
                impact: 'serious',
                detail: 'WCAG 2.5.8 requires minimum 44x44px touch targets for mobile usability'
            });
        }

        // Check for forms and their UX
        const forms = document.querySelectorAll('form');
        forms.forEach((form, i) => {
            const inputs = form.querySelectorAll('input, select, textarea');
            const labels = form.querySelectorAll('label');
            if (inputs.length > 8) {
                findings.push({
                    rule_id: 'ux/long-form',
                    description: `Form ${i + 1} has ${inputs.length} fields — consider breaking into steps`,
                    impact: 'moderate',
                    detail: 'Long forms increase drop-off rates'
                });
            }
        });

        // Check for skip-to-content link
        const firstLink = document.querySelector('a');
        const hasSkipLink = firstLink && (
            firstLink.textContent.toLowerCase().includes('skip') ||
            firstLink.getAttribute('href') === '#main' ||
            firstLink.getAttribute('href') === '#content'
        );
        if (!hasSkipLink) {
            findings.push({
                rule_id: 'ux/no-skip-link',
                description: 'No skip-to-content link found for keyboard users',
                impact: 'serious',
                detail: 'First focusable element should be a skip-to-main-content link'
            });
        }

        return findings;
    }""")

    for f in phase4_results:
        emit(scan_id, f"Found: {f['rule_id']}", f['description'], phase="Phase 4: UX & Performance")

    all_violations.extend([{**f, "category": "ux-performance"} for f in phase4_results])
    emit(scan_id, f"Phase 4 complete", f"{len(phase4_results)} issues found", phase="Phase 4: UX & Performance")

    # ── Phase 5: SEO & Discoverability ──
    emit(scan_id, "Phase 5: SEO & Discoverability", "Checking search engine optimization", phase="Phase 5: SEO")

    phase5_results = await page.evaluate("""() => {
        const findings = [];

        // Check meta title
        const title = document.querySelector('title');
        if (!title || !title.textContent.trim()) {
            findings.push({
                rule_id: 'seo/missing-title',
                description: 'No <title> tag found or it is empty',
                impact: 'critical',
                detail: 'Title tag is the most important on-page SEO element'
            });
        } else if (title.textContent.length > 60) {
            findings.push({
                rule_id: 'seo/title-too-long',
                description: `Title tag is ${title.textContent.length} characters — should be under 60`,
                impact: 'moderate',
                detail: `Title: "${title.textContent.substring(0, 80)}..."`
            });
        }

        // Check meta description
        const desc = document.querySelector('meta[name="description"]');
        if (!desc || !desc.content.trim()) {
            findings.push({
                rule_id: 'seo/missing-meta-description',
                description: 'No meta description tag found or it is empty',
                impact: 'serious',
                detail: 'Meta description is used by search engines in results snippets'
            });
        } else if (desc.content.length > 160) {
            findings.push({
                rule_id: 'seo/meta-description-long',
                description: `Meta description is ${desc.content.length} characters — should be under 160`,
                impact: 'minor',
                detail: `Description: "${desc.content.substring(0, 100)}..."`
            });
        }

        // Check canonical URL
        const canonical = document.querySelector('link[rel="canonical"]');
        if (!canonical) {
            findings.push({
                rule_id: 'seo/missing-canonical',
                description: 'No canonical URL specified — risk of duplicate content issues',
                impact: 'serious',
                detail: 'Add <link rel="canonical" href="..."> to specify the preferred URL'
            });
        }

        // Check heading hierarchy
        const h1s = document.querySelectorAll('h1');
        if (h1s.length === 0) {
            findings.push({
                rule_id: 'seo/missing-h1',
                description: 'No H1 heading found on the page',
                impact: 'critical',
                detail: 'Every page should have exactly one H1 describing its main topic'
            });
        } else if (h1s.length > 1) {
            findings.push({
                rule_id: 'seo/multiple-h1',
                description: `${h1s.length} H1 headings found — should have exactly one`,
                impact: 'serious',
                detail: 'Multiple H1s dilute page topic signals'
            });
        }

        // Check heading order
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        let skipped = false;
        for (let i = 1; i < headings.length; i++) {
            const prev = parseInt(headings[i-1].tagName[1]);
            const curr = parseInt(headings[i].tagName[1]);
            if (curr > prev + 1) { skipped = true; break; }
        }
        if (skipped) {
            findings.push({
                rule_id: 'seo/heading-hierarchy-skip',
                description: 'Heading hierarchy skips levels (e.g., H1 → H3)',
                impact: 'moderate',
                detail: 'Maintain sequential heading order: H1 → H2 → H3'
            });
        }

        // Check Open Graph tags
        const hasOG = !!document.querySelector('meta[property="og:title"]') &&
                      !!document.querySelector('meta[property="og:description"]');
        if (!hasOG) {
            findings.push({
                rule_id: 'seo/missing-opengraph',
                description: 'Missing Open Graph meta tags for social media sharing',
                impact: 'moderate',
                detail: 'Add og:title, og:description, og:image for proper social previews'
            });
        }

        // Check Twitter Card
        const hasTwitter = !!document.querySelector('meta[name="twitter:card"]');
        if (!hasTwitter) {
            findings.push({
                rule_id: 'seo/missing-twitter-card',
                description: 'Missing Twitter Card meta tags',
                impact: 'minor',
                detail: 'Add twitter:card, twitter:title, twitter:description meta tags'
            });
        }

        // Check for lang attribute
        const htmlLang = document.documentElement.getAttribute('lang');
        if (!htmlLang) {
            findings.push({
                rule_id: 'seo/missing-lang',
                description: 'No lang attribute on <html> element',
                impact: 'serious',
                detail: 'Add lang="en" (or appropriate language) to the <html> tag'
            });
        }

        return findings;
    }""")

    # robots.txt and sitemap.xml are per-origin, so only check them once per site
    if check_site_files:
        emit(scan_id, "Checking robots.txt & sitemap", "Fetching server configuration files", phase="Phase 5: SEO")

        robots_result = await page.evaluate("""async () => {
            const findings = [];
            try {
                const origin = window.location.origin;
                const robotsRes = await fetch(origin + '/robots.txt');
                if (!robotsRes.ok) {
                    findings.push({
                        rule_id: 'seo/missing-robots-txt',
                        description: 'No robots.txt file found — search engines need crawl directives',
                        impact: 'serious',
                        detail: `HTTP ${robotsRes.status} at ${origin}/robots.txt`
                    });
                } else {
                    const text = await robotsRes.text();
                    if (!text.toLowerCase().includes('sitemap')) {
                        findings.push({
                            rule_id: 'seo/robots-no-sitemap-ref',
                            description: 'robots.txt does not reference a sitemap.xml',
                            impact: 'moderate',
                            detail: 'Add Sitemap: directive to robots.txt'
                        });
                    }
                }
            } catch {}

            try {
                const origin = window.location.origin;
                const sitemapRes = await fetch(origin + '/sitemap.xml');
                if (!sitemapRes.ok) {
                    findings.push({
                        rule_id: 'seo/missing-sitemap',
                        description: 'No sitemap.xml found — submit one to search engines',
                        impact: 'serious',
                        detail: `HTTP ${sitemapRes.status} at ${origin}/sitemap.xml`
                    });
                }
            } catch {}

            return findings;
        }""")

        phase5_results.extend(robots_result)

    for f in phase5_results:
        emit(scan_id, f"Found: {f['rule_id']}", f['description'], phase="Phase 5: SEO")

    all_violations.extend([{**f, "category": "seo"} for f in phase5_results])
    emit(scan_id, f"Phase 5 complete", f"{len(phase5_results)} issues found", phase="Phase 5: SEO")

    # ── Phase 6: Baseline & Measurement ──
    emit(scan_id, "Phase 6: Baseline & Measurement", "Generating baseline metrics summary", phase="Phase 6: Baseline")

    total_non_axe = len(all_violations)
    total_axe = len(axe_violations)
    total_all = total_non_axe + total_axe

    phase6_results = await page.evaluate("""(totalIssues) => {
        const findings = [];
        const links = document.querySelectorAll('a[href]');
        const pages = new Set();
        links.forEach(a => {
            if (a.hostname === window.location.hostname) {
                pages.add(new URL(a.href).pathname);
            }
        });

        findings.push({
            rule_id: 'baseline/site-inventory',
            description: `${pages.size} unique internal pages linked from this page — map all for migration planning`,
            impact: 'minor',
            detail: 'Component inventory helps plan redirect migration to NOVA',
            paths: Array.from(pages).slice(0, 20)
        });

        return findings;
    }""", total_all)

    all_violations.extend([{**f, "category": "baseline"} for f in phase6_results])
    emit(scan_id, f"Phase 6 complete", f"Baseline established with {total_all} total issues across all phases", phase="Phase 6: Baseline")

    return {
        "axe_violations": axe_violations,
        "other_violations": all_violations,
        "passes": axe_passes,
    }


def _page_score(passes: int, axe_violation_count: int) -> float:
    total_checks = passes + axe_violation_count
    return round(passes / total_checks * 100, 1) if total_checks > 0 else 100.0


async def _save_page_violations(db, scan: Scan, page_url: str, audit: dict) -> int:
    saved = 0

    # Save axe-core violations (Phase 2) with elements
    for v_data in audit["axe_violations"]:
        standards_tags = [
            t for t in v_data.get("tags", [])
            if t.startswith("wcag") or t.startswith("section508")
        ]
        wcag_criteria = ", ".join(standards_tags) if standards_tags else "best-practice"

        violation = Violation(
            scan_id=scan.id,
            page_url=page_url,
            category="accessibility",
            rule_id=v_data.get("id", "unknown"),
            description=v_data.get("description", ""),
            impact=v_data.get("impact", "minor"),
            wcag_criteria=wcag_criteria,
            help_url=v_data.get("helpUrl"),
        )
        db.add(violation)
        await db.flush()
        saved += 1

        for node in v_data.get("nodes", []):
            db.add(AffectedElement(
                violation_id=violation.id,
                selector=", ".join(node.get("target", ["unknown"])),
                html=node.get("html", ""),
                failure_summary=node.get("failureSummary"),
            ))

    # Save other phase violations
    for v_data in audit["other_violations"]:
        violation = Violation(
            scan_id=scan.id,
            page_url=page_url,
            category=v_data.get("category", "other"),
            rule_id=v_data.get("rule_id", "unknown"),
            description=v_data.get("description", ""),
            impact=v_data.get("impact", "minor"),
            wcag_criteria=v_data.get("category", "other"),
            help_url=None,
        )
        db.add(violation)
        await db.flush()
        saved += 1

        if v_data.get("detail"):
            db.add(AffectedElement(
                violation_id=violation.id,
                selector="page-level",
                html="",
                failure_summary=v_data["detail"],
            ))

    return saved


NON_HTML_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".bmp", ".avif",
    ".zip", ".gz", ".tar", ".rar", ".7z", ".dmg", ".exe", ".msi", ".apk",
    ".mp3", ".mp4", ".mov", ".avi", ".webm", ".wav", ".ogg",
    ".css", ".js", ".json", ".xml", ".txt", ".csv", ".rss", ".atom",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".woff", ".woff2", ".ttf", ".eot",
)
MAX_SITEMAP_FILES = 5


def _site_host(host: str) -> str:
    host = host.lower()
    return host[4:] if host.startswith("www.") else host


def _site_id(url: str) -> str:
    """Host (ignoring www.) plus any non-default port; links must match a seed's site id to be crawled."""
    parsed = urlparse(url)
    try:
        port = parsed.port
    except ValueError:
        return ""
    host = _site_host(parsed.hostname or "")
    return f"{host}:{port}" if port not in (None, 80, 443) else host


def _page_key(url: str) -> str:
    """Identity used to avoid scanning the same page twice (ignores fragment, www., trailing slash)."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    key = f"{_site_host(parsed.hostname or '')}{path}"
    return f"{key}?{parsed.query}" if parsed.query else key


def _crawlable_link(href: str, allowed_hosts: set[str]) -> str | None:
    """Return a cleaned same-site page URL, or None if the link shouldn't be crawled."""
    try:
        parsed = urlparse(href.strip())
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    if _site_id(href.strip()) not in allowed_hosts:
        return None
    if (parsed.path or "/").lower().endswith(NON_HTML_EXTENSIONS):
        return None
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))


async def _sitemap_links(context, origin: str, allowed_hosts: set[str]) -> list[str]:
    """Page URLs listed in the origin's sitemap.xml (following sitemap indexes a few levels)."""
    pending = [f"{origin}/sitemap.xml"]
    fetched: set[str] = set()
    found: list[str] = []
    while pending and len(fetched) < MAX_SITEMAP_FILES:
        sitemap_url = pending.pop(0)
        if sitemap_url in fetched:
            continue
        fetched.add(sitemap_url)
        try:
            await asyncio.to_thread(validate_url, sitemap_url)
            response = await context.request.get(sitemap_url, timeout=15000)
            if not response.ok:
                continue
            body = await response.text()
        except Exception as e:
            logger.info("Sitemap %s unavailable: %s", sitemap_url, e)
            continue
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", body, re.IGNORECASE | re.DOTALL):
            loc = html.unescape(loc)
            parsed_loc = urlparse(loc)
            if parsed_loc.path.lower().endswith(".xml"):
                if parsed_loc.scheme in ("http", "https") and _site_id(loc) in allowed_hosts:
                    pending.append(loc)
            elif link := _crawlable_link(loc, allowed_hosts):
                found.append(link)
    return found


async def run_scan(scan_id: str, urls: list[str] | str, discover: bool = False) -> None:
    """Scan every URL in ``urls``. With ``discover``, also crawl same-site links and sitemap.xml."""
    if isinstance(urls, str):
        urls = [urls]
    urls = list(dict.fromkeys(u for u in urls if u))

    async with async_session() as db:
        scan = await db.get(Scan, UUID(scan_id))
        if not scan:
            logger.error("Scan %s not found", scan_id)
            return

        scan.status = "running"
        await db.commit()

        max_pages = max(settings.SCAN_ALL_MAX_PAGES, len(urls)) if discover else len(urls)
        allowed_hosts = {_site_id(u) for u in urls}
        queue: deque[str] = deque()
        seen: set[str] = set()

        def enqueue(url: str) -> bool:
            key = _page_key(url)
            if key in seen or len(seen) >= max_pages:
                return False
            seen.add(key)
            queue.append(url)
            return True

        for url in urls:
            enqueue(url)

        page_results: list[dict] = []

        def page_event(step: str, detail: str, index: int, page: dict, status: str = "running") -> None:
            emit(scan_id, step, detail, status=status, phase="Page",
                 page={"index": index, **page}, page_total=len(seen), discovering=discover)

        if discover:
            emit(scan_id, "Scan all pages", f"Discovering same-site pages (up to {max_pages})", phase="Setup")
        else:
            emit(scan_id, "Scan entered pages", f"{len(urls)} page(s) to scan", phase="Setup")

        try:
            from playwright.async_api import async_playwright

            emit(scan_id, "Launching browser", "Starting Chromium headless", phase="Setup")

            total_passes = 0
            total_axe = 0
            total_saved = 0
            checked_origins: set[str] = set()

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 720},
                    user_agent="AccessiAI Scanner/1.0",
                    # Lets axe-core be injected on pages whose CSP blocks third-party scripts
                    bypass_csp=True,
                )

                if discover:
                    origins = list(dict.fromkeys(
                        f"{urlparse(u).scheme}://{urlparse(u).netloc}" for u in urls
                    ))
                    for origin in origins:
                        added = sum(enqueue(link) for link in await _sitemap_links(context, origin, allowed_hosts))
                        if added:
                            emit(scan_id, "Sitemap read", f"{added} page(s) found in {origin}/sitemap.xml",
                                 phase="Setup", page_total=len(seen))

                index = 0
                while queue:
                    url = queue.popleft()
                    index += 1
                    page_event(f"Scanning page {index} of {len(seen)}", url, index, {"url": url, "status": "running"})

                    page = None
                    try:
                        await asyncio.to_thread(validate_url, url)
                        page = await context.new_page()
                        await page.goto(url, timeout=30000, wait_until="networkidle")
                        emit(scan_id, "Page loaded", url, phase="Setup")

                        if discover:
                            try:
                                hrefs = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
                            except Exception:
                                hrefs = []
                            added = sum(
                                enqueue(link) for href in hrefs
                                if (link := _crawlable_link(href, allowed_hosts))
                            )
                            if added:
                                emit(scan_id, "Discovered pages", f"{added} new page(s) linked from {url}",
                                     phase="Setup", page_total=len(seen))

                        origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                        audit = await _audit_page(page, scan_id, check_site_files=origin not in checked_origins)
                        checked_origins.add(origin)
                    except Exception as e:
                        logger.warning("Scan %s: page %s failed: %s", scan_id, url, e)
                        # Playwright appends a multi-line call log; the first line is the useful part
                        error = (str(e).strip().splitlines() or [type(e).__name__])[0]
                        result = {"url": url, "status": "failed", "score": None, "total_violations": 0, "error": error}
                        page_results.append(result)
                        page_event(f"Page {index} failed", f"{url}: {error}", index, result, status="page_failed")
                        continue
                    finally:
                        if page is not None:
                            await page.close()

                    saved = await _save_page_violations(db, scan, url, audit)
                    total_saved += saved
                    total_passes += audit["passes"]
                    total_axe += len(audit["axe_violations"])
                    result = {
                        "url": url,
                        "status": "completed",
                        "score": _page_score(audit["passes"], len(audit["axe_violations"])),
                        "total_violations": saved,
                        "error": None,
                    }
                    page_results.append(result)
                    page_event(f"Page {index} complete", f"{url} — score {result['score']:.0f}, {saved} issues",
                               index, result, status="page_completed")

                await browser.close()

            completed_pages = [r for r in page_results if r["status"] == "completed"]
            if not completed_pages:
                raise RuntimeError("All pages failed to scan")

            emit(scan_id, "Saving results", "Writing violations to database", phase="Saving")

            score = _page_score(total_passes, total_axe)
            scan.accessibility_score = score
            scan.total_violations = total_saved
            scan.page_results = page_results
            scan.status = "completed"
            scan.scan_completed_at = datetime.now(timezone.utc)
            await db.commit()

            emit(
                scan_id,
                "Scan complete",
                f"Score: {score:.1f}/100 — {total_saved} total issues across {len(completed_pages)} page(s)",
                status="completed",
                phase="Complete",
            )
            logger.info("Scan %s completed: score=%.1f, violations=%d, pages=%d", scan_id, score, total_saved, len(completed_pages))

        except Exception as e:
            await db.rollback()
            scan = await db.get(Scan, UUID(scan_id))
            if scan:
                scan.status = "failed"
                scan.page_results = page_results
                scan.scan_completed_at = datetime.now(timezone.utc)
                await db.commit()
            emit(scan_id, "Scan failed", str(e), status="failed", phase="Error")
            logger.exception("Scan %s failed: %s", scan_id, e)
