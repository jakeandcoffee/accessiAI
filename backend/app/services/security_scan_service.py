import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import uuid4

import httpx

from app.services.scan_progress import emit
from app.services.scan_service import validate_url

logger = logging.getLogger(__name__)

_security_results: dict[str, dict] = {}

_scan_mapping: dict[str, str] = {}


def register_security_scan(scan_id: str, security_scan_id: str) -> None:
    _scan_mapping[scan_id] = security_scan_id


def get_security_scan_id(scan_id: str) -> str | None:
    return _scan_mapping.get(scan_id)


SEVERITY_DEDUCTIONS = {
    "critical": 15,
    "high": 10,
    "medium": 5,
    "low": 2,
    "info": 0,
}

CATEGORY_LABELS = {
    "http-headers": "HTTP Security Headers",
    "ssl-tls": "SSL / TLS",
    "cookies": "Cookie Security",
    "content-security": "Content Security",
    "info-disclosure": "Information Disclosure",
}

PROBE_PATHS = [
    "/.env",
    "/debug",
    "/phpinfo.php",
    "/wp-admin",
    "/wp-login.php",
    "/.git/config",
    "/server-status",
    "/elmah.axd",
    "/trace.axd",
    "/.DS_Store",
]


def _finding(
    title: str,
    description: str,
    severity: str,
    category: str,
    recommendation: str,
    details: str = "",
) -> dict:
    return {
        "id": str(uuid4()),
        "title": title,
        "description": description,
        "severity": severity,
        "category": category,
        "recommendation": recommendation,
        "details": details,
    }


async def run_security_scan(scan_id: str, url: str) -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    findings: list[dict] = []

    emit(scan_id, "Validating URL", f"Checking {url}", phase="Setup")
    try:
        validate_url(url)
    except ValueError as e:
        emit(scan_id, "Validation failed", str(e), status="failed", phase="Error")
        _security_results[scan_id] = {
            "scan_id": scan_id,
            "url": url,
            "status": "failed",
            "error": str(e),
            "scan_started_at": started_at,
            "scan_completed_at": datetime.now(timezone.utc).isoformat(),
            "security_score": 0,
            "total_findings": 0,
            "categories": [],
            "findings": [],
        }
        return

    emit(scan_id, "URL validated", url, phase="Setup")
    parsed = urlparse(url)

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(20.0),
            verify=True,
        ) as client:
            emit(scan_id, "Fetching page", url, phase="Setup")
            response = await client.get(url)
            headers = response.headers

            # ── Phase 1: HTTP Security Headers ──
            emit(scan_id, "Phase 1: HTTP Security Headers", "Inspecting response headers", phase="Phase 1: HTTP Headers")

            header_checks = [
                ("Strict-Transport-Security", "strict-transport-security", "critical",
                 "Enable HSTS by adding Strict-Transport-Security header with max-age of at least 31536000"),
                ("Content-Security-Policy", "content-security-policy", "high",
                 "Define a Content-Security-Policy header to prevent XSS and data injection attacks"),
                ("X-Frame-Options", "x-frame-options", "high",
                 "Set X-Frame-Options to DENY or SAMEORIGIN to prevent clickjacking"),
                ("X-Content-Type-Options", "x-content-type-options", "medium",
                 "Set X-Content-Type-Options: nosniff to prevent MIME-type sniffing"),
                ("Referrer-Policy", "referrer-policy", "medium",
                 "Set Referrer-Policy to strict-origin-when-cross-origin or no-referrer"),
                ("Permissions-Policy", "permissions-policy", "medium",
                 "Set Permissions-Policy to restrict access to browser features like camera, microphone, geolocation"),
            ]

            for display_name, header_key, severity, recommendation in header_checks:
                value = headers.get(header_key)
                if not value:
                    f = _finding(
                        title=f"Missing {display_name}",
                        description=f"The {display_name} header is not set in the HTTP response.",
                        severity=severity,
                        category="http-headers",
                        recommendation=recommendation,
                    )
                    findings.append(f)
                    emit(scan_id, f"Missing: {display_name}", f"Header not found", phase="Phase 1: HTTP Headers")
                else:
                    emit(scan_id, f"Found: {display_name}", value[:120], phase="Phase 1: HTTP Headers")

            xss_prot = headers.get("x-xss-protection")
            if xss_prot:
                findings.append(_finding(
                    title="Deprecated X-XSS-Protection header present",
                    description="X-XSS-Protection is deprecated and can introduce vulnerabilities in older browsers.",
                    severity="info",
                    category="http-headers",
                    recommendation="Remove X-XSS-Protection and rely on Content-Security-Policy instead",
                    details=f"Value: {xss_prot}",
                ))
                emit(scan_id, "Found: X-XSS-Protection (deprecated)", xss_prot, phase="Phase 1: HTTP Headers")

            phase1_count = sum(1 for f in findings if f["category"] == "http-headers")
            emit(scan_id, "Phase 1 complete", f"{phase1_count} issues found", phase="Phase 1: HTTP Headers")

            # ── Phase 2: SSL/TLS Security ──
            emit(scan_id, "Phase 2: SSL/TLS Security", "Checking HTTPS and certificate", phase="Phase 2: SSL/TLS")

            if parsed.scheme == "https":
                emit(scan_id, "HTTPS enabled", "Site uses HTTPS", phase="Phase 2: SSL/TLS")
            else:
                emit(scan_id, "Checking HTTPS availability", "Testing HTTPS version of the site", phase="Phase 2: SSL/TLS")
                https_url = url.replace("http://", "https://", 1)
                try:
                    https_resp = await client.get(https_url, follow_redirects=True)
                    if https_resp.status_code < 400:
                        findings.append(_finding(
                            title="Site accessible over HTTP without redirect to HTTPS",
                            description="The site is served over HTTP but HTTPS is available. Visitors are not automatically redirected.",
                            severity="critical",
                            category="ssl-tls",
                            recommendation="Configure an automatic 301 redirect from HTTP to HTTPS",
                        ))
                        emit(scan_id, "No HTTPS redirect", "HTTPS available but HTTP does not redirect", phase="Phase 2: SSL/TLS")
                    else:
                        findings.append(_finding(
                            title="HTTPS not properly configured",
                            description=f"HTTPS returned status {https_resp.status_code}.",
                            severity="critical",
                            category="ssl-tls",
                            recommendation="Configure a valid SSL/TLS certificate and serve the site over HTTPS",
                        ))
                except Exception:
                    findings.append(_finding(
                        title="HTTPS not available",
                        description="The site does not support HTTPS connections.",
                        severity="critical",
                        category="ssl-tls",
                        recommendation="Obtain an SSL/TLS certificate and enable HTTPS",
                    ))
                    emit(scan_id, "HTTPS unavailable", "Could not connect over HTTPS", phase="Phase 2: SSL/TLS")

            if parsed.scheme == "https" or parsed.scheme == "http":
                try:
                    http_url = url if parsed.scheme == "http" else url.replace("https://", "http://", 1)
                    http_resp = await client.get(http_url, follow_redirects=False)
                    if http_resp.status_code in (301, 302, 307, 308):
                        location = http_resp.headers.get("location", "")
                        if location.startswith("https://"):
                            emit(scan_id, "HTTP redirects to HTTPS", location[:120], phase="Phase 2: SSL/TLS")
                        else:
                            findings.append(_finding(
                                title="HTTP does not redirect to HTTPS",
                                description="HTTP requests are not redirected to the secure HTTPS version.",
                                severity="high",
                                category="ssl-tls",
                                recommendation="Configure a 301 redirect from HTTP to HTTPS",
                                details=f"Redirect location: {location}",
                            ))
                    elif parsed.scheme == "https":
                        pass
                except Exception:
                    pass

            phase2_count = sum(1 for f in findings if f["category"] == "ssl-tls")
            emit(scan_id, "Phase 2 complete", f"{phase2_count} issues found", phase="Phase 2: SSL/TLS")

            # ── Phase 3: Cookie Security ──
            emit(scan_id, "Phase 3: Cookie Security", "Inspecting Set-Cookie headers", phase="Phase 3: Cookies")

            set_cookie_headers = response.headers.get_list("set-cookie") if hasattr(response.headers, "get_list") else []
            if not set_cookie_headers:
                raw_cookies = [v for k, v in response.headers.multi_items() if k.lower() == "set-cookie"]
                set_cookie_headers = raw_cookies

            if not set_cookie_headers:
                emit(scan_id, "No cookies set", "No Set-Cookie headers in response", phase="Phase 3: Cookies")
            else:
                for cookie_str in set_cookie_headers:
                    parts = cookie_str.split(";")
                    cookie_name = parts[0].split("=")[0].strip() if parts else "unknown"
                    flags_lower = cookie_str.lower()

                    if "httponly" not in flags_lower:
                        findings.append(_finding(
                            title=f"Cookie '{cookie_name}' missing HttpOnly flag",
                            description="Cookie is accessible to JavaScript, increasing XSS risk.",
                            severity="high",
                            category="cookies",
                            recommendation=f"Add the HttpOnly flag to the '{cookie_name}' cookie",
                            details=cookie_str[:200],
                        ))
                        emit(scan_id, f"Missing HttpOnly: {cookie_name}", "", phase="Phase 3: Cookies")

                    if "secure" not in flags_lower:
                        findings.append(_finding(
                            title=f"Cookie '{cookie_name}' missing Secure flag",
                            description="Cookie can be transmitted over unencrypted HTTP connections.",
                            severity="high",
                            category="cookies",
                            recommendation=f"Add the Secure flag to the '{cookie_name}' cookie",
                            details=cookie_str[:200],
                        ))
                        emit(scan_id, f"Missing Secure: {cookie_name}", "", phase="Phase 3: Cookies")

                    if "samesite" not in flags_lower:
                        findings.append(_finding(
                            title=f"Cookie '{cookie_name}' missing SameSite attribute",
                            description="Cookie lacks SameSite attribute, may be vulnerable to CSRF attacks.",
                            severity="medium",
                            category="cookies",
                            recommendation=f"Add SameSite=Lax or SameSite=Strict to the '{cookie_name}' cookie",
                            details=cookie_str[:200],
                        ))
                        emit(scan_id, f"Missing SameSite: {cookie_name}", "", phase="Phase 3: Cookies")

            phase3_count = sum(1 for f in findings if f["category"] == "cookies")
            emit(scan_id, "Phase 3 complete", f"{phase3_count} issues found", phase="Phase 3: Cookies")

            # ── Phase 4: Content Security (Playwright) ──
            emit(scan_id, "Phase 4: Content Security", "Launching browser for client-side checks", phase="Phase 4: Content Security")

            try:
                from playwright.async_api import async_playwright

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 720},
                        user_agent="AccessiAI SecurityScanner/1.0",
                    )
                    page = await context.new_page()
                    await page.goto(url, timeout=30000, wait_until="networkidle")

                    emit(scan_id, "Checking inline scripts", "Looking for scripts without nonce/hash", phase="Phase 4: Content Security")

                    content_results = await page.evaluate("""() => {
                        const findings = [];

                        // Inline scripts without nonce or hash
                        const inlineScripts = Array.from(document.querySelectorAll('script:not([src])'));
                        const unsafeInline = inlineScripts.filter(s => !s.nonce && !s.getAttribute('nonce'));
                        if (unsafeInline.length > 0) {
                            findings.push({
                                title: `${unsafeInline.length} inline script(s) without nonce attribute`,
                                description: 'Inline scripts without CSP nonce or hash are vulnerable to XSS injection.',
                                severity: 'high',
                                category: 'content-security',
                                recommendation: 'Add nonce attributes to inline scripts and configure CSP with matching nonces',
                                details: `${unsafeInline.length} unsafe inline scripts found`
                            });
                        }

                        // External scripts without SRI
                        const extScripts = Array.from(document.querySelectorAll('script[src]'));
                        const noSRI = extScripts.filter(s => {
                            const src = s.getAttribute('src') || '';
                            return !s.integrity && !src.startsWith('/') && !src.startsWith(window.location.origin);
                        });
                        if (noSRI.length > 0) {
                            findings.push({
                                title: `${noSRI.length} external script(s) without Subresource Integrity`,
                                description: 'External scripts loaded without integrity hashes could be tampered with.',
                                severity: 'medium',
                                category: 'content-security',
                                recommendation: 'Add integrity attributes with SHA-384 hashes to external script tags',
                                details: noSRI.map(s => s.src).slice(0, 5).join(', ')
                            });
                        }

                        // Mixed content
                        if (window.location.protocol === 'https:') {
                            const allResources = Array.from(document.querySelectorAll('[src], [href]'));
                            const mixed = allResources.filter(el => {
                                const attr = el.getAttribute('src') || el.getAttribute('href') || '';
                                return attr.startsWith('http://') && !attr.startsWith('http://localhost');
                            });
                            if (mixed.length > 0) {
                                findings.push({
                                    title: `${mixed.length} mixed content resource(s) detected`,
                                    description: 'HTTP resources loaded on an HTTPS page compromise the security of the connection.',
                                    severity: 'high',
                                    category: 'content-security',
                                    recommendation: 'Load all resources over HTTPS or use protocol-relative URLs',
                                    details: mixed.map(el => (el.getAttribute('src') || el.getAttribute('href'))).slice(0, 5).join(', ')
                                });
                            }
                        }

                        // Forms without CSRF tokens
                        const forms = Array.from(document.querySelectorAll('form'));
                        const noCsrf = forms.filter(form => {
                            const hasToken = !!form.querySelector('input[name*="csrf"]') ||
                                             !!form.querySelector('input[name*="token"]') ||
                                             !!form.querySelector('input[name="_token"]') ||
                                             !!form.querySelector('input[name="authenticity_token"]');
                            return !hasToken && form.method.toUpperCase() === 'POST';
                        });
                        if (noCsrf.length > 0) {
                            findings.push({
                                title: `${noCsrf.length} POST form(s) without CSRF token`,
                                description: 'Forms submitting data via POST without CSRF protection are vulnerable to cross-site request forgery.',
                                severity: 'high',
                                category: 'content-security',
                                recommendation: 'Add CSRF tokens to all POST forms',
                                details: noCsrf.map(f => f.action || 'inline').slice(0, 5).join(', ')
                            });
                        }

                        // External form actions
                        const extForms = forms.filter(form => {
                            const action = form.getAttribute('action') || '';
                            return action.startsWith('http') && !action.startsWith(window.location.origin);
                        });
                        if (extForms.length > 0) {
                            findings.push({
                                title: `${extForms.length} form(s) submit to external domains`,
                                description: 'Forms sending data to third-party domains may leak sensitive information.',
                                severity: 'medium',
                                category: 'content-security',
                                recommendation: 'Review external form actions and ensure data is sent to trusted domains only',
                                details: extForms.map(f => f.action).slice(0, 5).join(', ')
                            });
                        }

                        return findings;
                    }""")

                    for f in content_results:
                        findings.append(_finding(**f))
                        emit(scan_id, f"Found: {f['title'][:60]}", f.get("details", ""), phase="Phase 4: Content Security")

                    await browser.close()

            except Exception as e:
                logger.warning("Playwright content check failed for %s: %s", scan_id, e)
                emit(scan_id, "Browser check skipped", str(e)[:120], phase="Phase 4: Content Security")

            phase4_count = sum(1 for f in findings if f["category"] == "content-security")
            emit(scan_id, "Phase 4 complete", f"{phase4_count} issues found", phase="Phase 4: Content Security")

            # ── Phase 5: Information Disclosure ──
            emit(scan_id, "Phase 5: Information Disclosure", "Checking for exposed server info", phase="Phase 5: Info Disclosure")

            server = headers.get("server", "")
            if server:
                import re
                if re.search(r"\d+\.\d+", server):
                    findings.append(_finding(
                        title="Server header reveals version information",
                        description=f"The Server header exposes software version: {server}",
                        severity="medium",
                        category="info-disclosure",
                        recommendation="Remove or obfuscate version information from the Server header",
                        details=f"Server: {server}",
                    ))
                    emit(scan_id, "Server version exposed", server, phase="Phase 5: Info Disclosure")
                else:
                    emit(scan_id, "Server header present", server, phase="Phase 5: Info Disclosure")

            powered_by = headers.get("x-powered-by")
            if powered_by:
                findings.append(_finding(
                    title="X-Powered-By header exposes technology stack",
                    description=f"The X-Powered-By header reveals: {powered_by}",
                    severity="low",
                    category="info-disclosure",
                    recommendation="Remove the X-Powered-By header from server responses",
                    details=f"X-Powered-By: {powered_by}",
                ))
                emit(scan_id, "X-Powered-By exposed", powered_by, phase="Phase 5: Info Disclosure")

            emit(scan_id, "Probing sensitive paths", f"Checking {len(PROBE_PATHS)} common paths", phase="Phase 5: Info Disclosure")

            base = f"{parsed.scheme}://{parsed.netloc}"
            for path in PROBE_PATHS:
                try:
                    probe_resp = await client.get(f"{base}{path}", follow_redirects=False)
                    if probe_resp.status_code == 200:
                        findings.append(_finding(
                            title=f"Sensitive path accessible: {path}",
                            description=f"The path {path} returned HTTP 200 and may expose sensitive information.",
                            severity="critical" if path in ("/.env", "/.git/config") else "high",
                            category="info-disclosure",
                            recommendation=f"Block access to {path} in your web server configuration",
                            details=f"HTTP {probe_resp.status_code} at {base}{path}",
                        ))
                        emit(scan_id, f"Exposed: {path}", f"HTTP {probe_resp.status_code}", phase="Phase 5: Info Disclosure")
                except Exception:
                    pass

            phase5_count = sum(1 for f in findings if f["category"] == "info-disclosure")
            emit(scan_id, "Phase 5 complete", f"{phase5_count} issues found", phase="Phase 5: Info Disclosure")

        # ── Phase 6: Scoring ──
        emit(scan_id, "Calculating security score", "Tallying findings by severity", phase="Scoring")

        score = 100
        for f in findings:
            score -= SEVERITY_DEDUCTIONS.get(f["severity"], 0)
        score = max(0, score)

        completed_at = datetime.now(timezone.utc).isoformat()

        grouped: dict[str, list[dict]] = {}
        for f in findings:
            grouped.setdefault(f["category"], []).append(f)

        categories = []
        for cat_key, cat_findings in grouped.items():
            cat_score = 100
            for f in cat_findings:
                cat_score -= SEVERITY_DEDUCTIONS.get(f["severity"], 0)
            cat_score = max(0, cat_score)
            categories.append({
                "name": CATEGORY_LABELS.get(cat_key, cat_key),
                "score": cat_score,
                "findings": cat_findings,
            })

        _security_results[scan_id] = {
            "scan_id": scan_id,
            "url": url,
            "status": "completed",
            "scan_started_at": started_at,
            "scan_completed_at": completed_at,
            "security_score": score,
            "total_findings": len(findings),
            "categories": categories,
            "findings": findings,
        }

        emit(
            scan_id,
            "Security scan complete",
            f"Score: {score}/100 — {len(findings)} findings across {len(grouped)} categories",
            status="completed",
            phase="Complete",
        )
        logger.info("Security scan %s completed: score=%d, findings=%d", scan_id, score, len(findings))

    except Exception as e:
        _security_results[scan_id] = {
            "scan_id": scan_id,
            "url": url,
            "status": "failed",
            "error": str(e),
            "scan_started_at": started_at,
            "scan_completed_at": datetime.now(timezone.utc).isoformat(),
            "security_score": 0,
            "total_findings": 0,
            "categories": [],
            "findings": [],
        }
        emit(scan_id, "Security scan failed", str(e), status="failed", phase="Error")
        logger.exception("Security scan %s failed: %s", scan_id, e)


def get_results(scan_id: str) -> dict | None:
    return _security_results.get(scan_id)
