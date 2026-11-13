# AccessiAI

*Full-stack portfolio project · SaaS application*

AI-Powered Accessibility Audit Platform

Automatically scan websites for accessibility issues, identify WCAG and Section 508-tagged findings, and use AI to explain problems and recommend code fixes.

React + TypeScript · Tailwind CSS · Python + FastAPI · GraphQL · PostgreSQL · WCAG 2.2 AA · Section 508

## Contents

- [1. Project overview](#overview)
- [2. Core features](#features)
- [3. Technical architecture](#architecture)
- [4. Database design](#database)
- [5. Frontend structure](#frontend)
- [6. Backend structure](#backend)
- [7. WCAG and Section 508 requirements](#wcag)
- [8. Security](#security)
- [9. Testing strategy](#testing)
- [10. Development roadmap](#roadmap)
- [11. Deployment](#deployment)
- [12. GitHub structure](#github)
- [13. Resume description](#resume)
- [14. Success criteria](#success)
- [15. Implementation priorities](#priorities)
- [16. 6-Phase scan engine](#scan-phases)
- [17. Final objective](#objective)

<a id="overview"></a>

## 1. Project Overview

### 1.1 What is AccessiAI?

AccessiAI is an AI-powered web accessibility auditing platform that helps developers, designers, and businesses identify and fix accessibility problems on their websites.

Users can enter a website URL, run an automated accessibility scan, review WCAG and Section 508-tagged findings, receive AI-generated explanations, and track their remediation progress. The platform provides a centralized dashboard for managing website accessibility.

### 1.2 Problem Statement

Many websites contain accessibility problems that make them difficult for people with disabilities to use. Common problems include:

- Missing image alternative text.
- Insufficient color contrast.
- Missing form labels.
- Incorrect heading structures.
- Improper ARIA attributes.
- Keyboard navigation problems.
- Inaccessible buttons and links.
- Incorrect semantic HTML.

AccessiAI simplifies investigation by combining automated accessibility testing with AI-powered explanations and remediation suggestions.

### 1.3 Target Users

- Frontend and web developers.
- UI/UX designers.
- Accessibility specialists.
- Software development teams.
- Small and medium-sized businesses.

<a id="features"></a>

## 2. Core Features

### 2.1 User Authentication

- User registration and login.
- JWT authentication and secure password hashing.
- Logout and protected routes.
- User profile management.
- Role-based authorization.

### 2.2 Website Management

Users can add, edit, delete, and view multiple websites, see each website's latest accessibility score, review scan history, and launch new scans.

| Website | Latest score | Last scanned | Status |
| --- | --- | --- | --- |
| example.com | 92/100 | Nov 10 | Good |
| company.com | 67/100 | Nov 9 | Needs improvement |
| shop.com | 45/100 | Nov 8 | Poor |

### 2.3 Website Accessibility Scanner

1. User enters a website URL.
2. Backend validates the URL and applies security restrictions.
3. Playwright opens the website in a controlled browser.
4. axe-core analyzes the rendered page.
5. Accessibility violations and affected elements are collected.
6. Results are saved in PostgreSQL.
7. Frontend displays the results.

The scanner should collect the rule ID, description, impact, applicable WCAG and Section 508 tags, affected elements, CSS selector, HTML snippet, remediation guidance, and documentation URL.

| Rule | Impact | WCAG |
| --- | --- | --- |
| image-alt | Critical | 1.1.1 |
| color-contrast | Serious | 1.4.3 |
| label | Critical | 3.3.2 |
| button-name | Critical | 4.1.2 |

> **Important:** Automated scanning detects many issues but cannot establish complete WCAG or Section 508 compliance. Manual testing is also required.

### 2.4 Accessibility Dashboard

Display overall accessibility score, total scans, total violations, critical/serious/moderate/minor counts, historical score trends, recently scanned websites, and recently discovered issues.

```
ACCESSIBILITY DASHBOARD

Overall Score: 82 / 100

Total Websites:       5
Total Scans:         24
Total Violations:    37

Critical:             5
Serious:             12
Moderate:            15
Minor:                5

SCORE HISTORY
Website       Previous       Current
example.com      65            82
company.com      70            91
shop.com         40            58
```

Label the score as an internal progress indicator, not an official WCAG certification.

### 2.5 Accessibility Issue Management

- View and search violations.
- Filter by severity and WCAG criteria.
- Search by rule ID.
- Inspect affected HTML elements and code snippets.
- Mark issues as Open, In Progress, Resolved, or Ignored.
- Add notes and track remediation progress.

### 2.6 AI-Powered Accessibility Assistant

Integrate the OpenAI API so users can select a violation and request an explanation, an explanation of the affected WCAG criteria, suggested HTML or React fixes, the user impact, and testing recommendations.

**Detected issue**

```
<img src="product.jpg">
```

**Suggested fix**

```
<img
  src="product.jpg"
  alt="Blue running shoes"
>
```

AI suggestions must be reviewed by developers. AI must not claim generated fixes guarantee compliance. Avoid sending sensitive website information to external AI services and provide a fallback when the AI service is unavailable.

### 2.7 Accessibility Reports

Reports should include website URL, scan date, score, WCAG version and target, applicable Section 508 tags, total violations, severity breakdown, violation details, AI suggestions, and remediation status. Support PDF and JSON exports.

### 2.8 Scan History

Show scan date, duration, website URL, violation count, previous and current score, and comparisons between scans.

<a id="architecture"></a>

## 3. Technical Architecture

### 3.1 Architecture Overview

```
                   ACCESSIAI
                       |
             React + TypeScript
                 Tailwind CSS
                       |
                TanStack Query
                       |
                API Communication
                       |
             ---------------------
             |                   |
          REST API           GraphQL API
             |                   |
           FastAPI          Strawberry
             |                   |
             ---------------------
                       |
                 Python Services
                       |
          ---------------------------
          |            |            |
       Scanner        AI         Reports
          |            |            |
       Playwright   OpenAI API   PDF Engine
       axe-core
          |
       SQLAlchemy
          |
      PostgreSQL
```

### 3.2 Frontend Architecture

**Technologies:** React, TypeScript, Tailwind CSS, React Router, TanStack Query, Recharts, React Hook Form, and Zod.

**Responsibilities:** render the UI, handle interactions and routing, communicate with APIs, display scan results and analytics, validate forms, and implement accessible components.

### 3.3 Backend Architecture

**Technologies:** Python, FastAPI, Strawberry GraphQL, SQLAlchemy, PostgreSQL, Pydantic, and JWT.

**Why FastAPI:** It provides typed, validated REST endpoints and automatically generated API documentation. Its async support suits I/O-heavy work such as Playwright scans and asynchronous database access. FastAPI also integrates with Strawberry so the backend can offer GraphQL alongside REST.

**Responsibilities:** authentication, website and scan management, accessibility analysis, database operations, AI integration, report generation, and API authorization.

### 3.4 REST API and GraphQL Responsibilities

Use REST for resource operations and commands; use GraphQL for flexible dashboard queries and related data retrieval.

#### REST API examples

```
POST   /api/auth/register
POST   /api/auth/login

POST   /api/websites
GET    /api/websites
GET    /api/websites/{website_id}
PUT    /api/websites/{website_id}
DELETE /api/websites/{website_id}

POST   /api/websites/{website_id}/scans
GET    /api/scans/{scan_id}
GET    /api/scans/{scan_id}/report

POST   /api/violations/{violation_id}/ai-analysis
PATCH  /api/violations/{violation_id}/status

GET    /api/reports/{report_id}/download
```

#### GraphQL dashboard query

```
query GetDashboard {
  dashboard {
    totalWebsites
    totalScans
    totalViolations
    accessibilityScore
    severityBreakdown {
      severity
      count
    }
    recentScans {
      id
      websiteUrl
      score
      scanDate
      totalViolations
    }
  }
}
```

#### GraphQL violations query

```
query GetViolations($websiteId: ID!) {
  violations(websiteId: $websiteId) {
    id
    ruleId
    description
    impact
    wcagCriteria
    status
    affectedElements {
      selector
      html
    }
  }
}
```

<a id="database"></a>

## 4. Database Design

Use PostgreSQL with SQLAlchemy.

| Table | Fields |
| --- | --- |
| **Users** | id (UUID, PK), email, password_hash, full_name, role, created_at |
| **Websites** | id (UUID, PK), user_id (FK), name, url, created_at |
| **Scans** | id (UUID, PK), website_id (FK), status, accessibility_score, total_violations, scan_started_at, scan_completed_at |
| **Violations** | id (UUID, PK), scan_id (FK), rule_id, description, impact, wcag_criteria, status, help_url, created_at |
| **Affected Elements** | id (UUID, PK), violation_id (FK), selector, html, failure_summary |
| **AI Analyses** | id (UUID, PK), violation_id (FK), explanation, suggested_fix, model_name, created_at |
| **Issue Comments** | id (UUID, PK), violation_id (FK), user_id (FK), comment, created_at |

### 4.1 Database Relationships

```
User 1 ─── N Websites
Website 1 ─── N Scans
Scan 1 ─── N Violations
Violation 1 ─── N Affected Elements
Violation 1 ─── N AI Analyses
Violation 1 ─── N Issue Comments
User 1 ─── N Issue Comments
```

<a id="frontend"></a>

## 5. Frontend Folder Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   ├── layout/
│   │   ├── dashboard/
│   │   ├── websites/
│   │   ├── scanner/
│   │   ├── violations/
│   │   └── accessibility/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Websites.tsx
│   │   ├── WebsiteDetails.tsx
│   │   ├── ScanResults.tsx
│   │   ├── Violations.tsx
│   │   ├── Reports.tsx
│   │   └── Settings.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useWebsites.ts
│   │   └── useScans.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── websiteService.ts
│   │   └── scanService.ts
│   ├── graphql/
│   │   ├── queries/
│   │   └── mutations/
│   ├── context/
│   ├── types/
│   ├── utils/
│   ├── routes/
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

<a id="backend"></a>

## 6. Backend Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── websites.py
│   │   │   ├── scans.py
│   │   │   ├── violations.py
│   │   │   └── reports.py
│   │   └── dependencies.py
│   ├── graphql/
│   │   ├── schema.py
│   │   ├── queries.py
│   │   ├── mutations.py
│   │   └── types.py
│   ├── models/
│   │   ├── user.py
│   │   ├── website.py
│   │   ├── scan.py
│   │   ├── violation.py
│   │   └── comment.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── website.py
│   │   └── scan.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── website_service.py
│   │   ├── scan_service.py
│   │   ├── accessibility_service.py
│   │   ├── ai_service.py
│   │   └── report_service.py
│   ├── scanner/
│   │   ├── browser.py
│   │   ├── axe_runner.py
│   │   └── result_parser.py
│   ├── database/
│   │   ├── connection.py
│   │   └── base.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── permissions.py
│   └── main.py
├── migrations/
├── tests/
├── requirements.txt
└── .env.example
```

<a id="wcag"></a>

## 7. WCAG and Section 508 Accessibility Requirements

**Target:** WCAG 2.2 Level AA, with automated Section 508-tagged checks. The AccessiAI application itself must demonstrate accessibility best practices.

### 7.1 Semantic HTML

Use appropriate elements such as `header`, `nav`, `main`, `section`, `article`, `footer`, `button`, `form`, and `label`. Avoid using generic div elements for everything.

### 7.2 Keyboard Navigation

- Tab and Shift + Tab navigation.
- Enter and Space activation where appropriate.
- Escape to close dialogs.
- Visible focus indicators and logical focus order.
- No keyboard traps.

### 7.3 Screen Reader Support

- Meaningful accessible names.
- Appropriate ARIA attributes when native HTML is insufficient.
- Accessible form labels and error messages.
- Announcements for dynamic content.
- Proper dialog semantics.

### 7.4 Color Contrast

- At least 4.5:1 for normal text.
- At least 3:1 for large text.
- Check non-text contrast for relevant controls and graphical objects.

### 7.5 Forms

- Every input has an accessible label.
- Required fields are identified.
- Validation errors are clearly communicated and associated with inputs.
- Instructions are available before submission.

### 7.6 Responsive Design

Support desktop, laptop, tablet, and mobile layouts, including zoom and reflow without loss of functionality.

### 7.7 Accessibility Testing

Use axe-core, Playwright, Lighthouse, NVDA screen reader, and keyboard-only testing. Test the AccessiAI application itself, not just the websites it scans.

### 7.8 Section 508

Run axe-core's `section508`-tagged rules alongside WCAG 2.2 A/AA checks. Section 508 applies to U.S. federal agencies and their ICT; its Revised Standards incorporate WCAG 2.0 Level A and AA for web content and include requirements that automated web scans cannot fully assess.

Store and display applicable Section 508 tags with each finding. Treat automated results as a technical screening aid, not a Section 508 conformance determination. Document and perform manual testing for keyboard operation, assistive-technology workflows, documents, and other applicable requirements.

<a id="security"></a>

## 8. Security Requirements

- Password hashing using Argon2id or bcrypt.
- JWT authentication with appropriate expiration.
- Authorization checks for every user-owned resource.
- Input validation using Pydantic.
- SQL injection prevention through SQLAlchemy.
- Rate limiting and CORS restrictions.
- Environment variables for API keys.
- Secure error handling and HTTPS in production.

### Scanner Security — SSRF Protection

Because the platform scans external websites, the scanning service must protect against Server-Side Request Forgery (SSRF).

- Allow only HTTP and HTTPS.
- Block localhost, private IP ranges, and cloud metadata endpoints.
- Validate DNS resolution and revalidate redirects.
- Restrict browser access to internal networks.
- Limit scan duration and resource consumption.
- Run browser workers in isolated environments.
- Apply page and response size limits.

> **Security rule:** Never allow an arbitrary website to use the scanner to access internal infrastructure.

<a id="testing"></a>

## 9. Testing Strategy

### Frontend Testing

**Tools:** Vitest, React Testing Library, axe-core, Playwright.

Test component rendering, form validation, authentication flows, API error handling, dashboard data, keyboard navigation, screen reader accessibility, and responsive layouts.

### Backend Testing

**Tools:** Pytest, HTTPX, pytest-asyncio.

Test authentication, authorization, REST endpoints, GraphQL queries and mutations, database relationships, scanner results, AI service failures, report generation, and SSRF protections.

### End-to-End Testing

1. Register a user.
2. Log in.
3. Add a website.
4. Run an accessibility scan.
5. View violations.
6. Request AI analysis.
7. Update an issue status.
8. Generate a PDF report.

<a id="roadmap"></a>

## 10. Development Roadmap

| Phase | Tasks | Deliverable |
| --- | --- | --- |
| 1 | Project setup, React, Tailwind, FastAPI | Running application |
| 2 | Dashboard and responsive UI | Frontend MVP |
| 3 | PostgreSQL and SQLAlchemy | Database integration |
| 4 | Authentication and authorization | Secure login |
| 5 | REST API and GraphQL | API integration |
| 6 | Playwright and axe-core | Website scanner |
| 7 | Violation management | Issue tracking |
| 8 | OpenAI integration | AI assistant |
| 9 | PDF and JSON reports | Reporting |
| 10 | WCAG testing and security | Quality assurance |
| 11 | Deployment | Live application |

Suggested timeline: approximately 6–8 weeks, depending on development time and AI-assisted implementation.

<a id="deployment"></a>

## 11. Deployment Architecture

### Frontend — Vercel

- Host React application.
- Configure production environment variables.
- Connect frontend to backend API.
- Configure custom domain.

### Backend — Render or equivalent

- Host FastAPI and Strawberry GraphQL.
- Run Playwright scanning workers.
- Connect to PostgreSQL.
- Configure secure environment variables.

### Database

Use managed PostgreSQL.

### Environment Variables

```
# Database
DATABASE_URL=

# Authentication
JWT_SECRET_KEY=

# OpenAI
OPENAI_API_KEY=

# Application
FRONTEND_URL=
BACKEND_URL=

# Security
ALLOWED_ORIGINS=
```

Never commit actual API keys or secrets to GitHub.

<a id="github"></a>

## 12. GitHub Repository Structure

```
accessiai/
├── frontend/
├── backend/
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── api-documentation.md
│   ├── accessibility.md
│   └── security.md
├── screenshots/
├── README.md
├── CLAUDE.md
├── .gitignore
└── docker-compose.yml
```

Include clear installation instructions, architecture documentation, API documentation, database diagrams, screenshots, demo credentials if applicable, example environment variables, and testing instructions.

<a id="resume"></a>

## 13. Resume Description

### AI-Powered Accessibility Audit Platform — AccessiAI

**Technologies:** ReactJS, TypeScript, Tailwind CSS, Python, FastAPI, GraphQL, Strawberry, PostgreSQL, SQLAlchemy, OpenAI API, Playwright, axe-core.

- Developed a full-stack accessibility auditing platform using ReactJS, Tailwind CSS, Python, and FastAPI.
- Designed RESTful APIs and GraphQL endpoints for website scanning, dashboard analytics, and accessibility issue management.
- Integrated Playwright and axe-core to automate WCAG testing and detect Section 508-tagged accessibility findings.
- Implemented AI-powered accessibility analysis to explain violations and generate suggested code remediation.
- Developed responsive and accessible UI components following WCAG 2.2 AA guidelines.
- Implemented JWT authentication, database relationships, and interactive reporting dashboards using PostgreSQL.

> Only list features that have actually been implemented and verified.

<a id="success"></a>

## 14. Project Success Criteria

Check off items as they are completed. Your progress stays available while this page remains open.

- [ ] Users can register and log in.
- [ ] Users can manage multiple websites.
- [ ] Users can scan publicly accessible websites safely.
- [ ] Accessibility violations are detected and stored.
- [ ] Dashboard displays scan results and trends.
- [ ] Users can filter and manage violations.
- [ ] AI explains accessibility issues.
- [ ] AI generates remediation suggestions.
- [ ] REST APIs work correctly.
- [ ] GraphQL queries and mutations work correctly.
- [ ] PostgreSQL stores application data.
- [ ] Users can export PDF reports.
- [ ] Application supports keyboard navigation.
- [ ] Automated accessibility checks are passing for applicable tested criteria.
- [ ] Manual WCAG and applicable Section 508 testing is documented.
- [ ] Application is deployed and accessible through a live URL.
- [ ] GitHub repository contains documentation and screenshots.

<a id="priorities"></a>

## 15. Recommended Implementation Priorities

**MVP — Build First**

1. React dashboard.
2. FastAPI backend.
3. PostgreSQL database.
4. JWT authentication.
5. Website management.
6. Playwright + axe-core scanner.
7. Violation dashboard.
8. WCAG 2.2 AA and Section 508-tagged checks.

**Advanced Features — Build Second**

1. GraphQL integration.
2. OpenAI-powered explanations.
3. AI-generated React/HTML fixes.
4. Scan history comparison.
5. PDF reports.
6. Advanced analytics.

**Portfolio Polish — Build Last**

1. Responsive design.
2. Comprehensive accessibility testing.
3. Unit and integration tests.
4. End-to-end tests.
5. Docker configuration.
6. Production deployment.
7. GitHub documentation and screenshots.

<a id="scan-phases"></a>

## 16. 6-Phase Scan Engine

Every scan runs six sequential audit phases via Playwright and reports findings in real-time through Server-Sent Events (SSE). Each violation is categorized by phase so results can be grouped and prioritized.

### Phase 1 — Data Quality & Measurement

Category: `data-quality`

| Check | What it detects |
| --- | --- |
| GTM / GA4 presence | Missing Google Tag Manager or GA4 tracking scripts |
| Duplicate tracking scripts | Analytics scripts loaded more than once (causes double-counted events) |
| dataLayer object | Missing `window.dataLayer` required for GTM event tracking |
| UTM consistency | Excessive `utm_medium` variants across outbound links |
| Form event tracking | Forms without detectable `form_start` / `form_submit` events |
| Site search tracking | Search inputs present but no `view_search_results` event |

### Phase 2 — Accessibility Audit (WCAG 2.2 AA + Section 508)

Category: `accessibility` · Engine: axe-core 4.10

| Check | What it detects |
| --- | --- |
| Color contrast | Text/background combos below 4.5:1 (AA) ratio |
| Alt text | Missing or empty `alt` attributes on non-decorative images |
| Form accessibility | Missing labels, error messages, and focus management |
| Keyboard navigation | Tab order, visible focus indicators, skip-to-content links |
| ARIA landmarks | Missing `<main>`, `<nav>`, sequential heading hierarchy |
| WCAG 2.x rule set | wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa tags |
| Section 508 rules | axe-core `section508`-tagged checks; findings retain their applicable WCAG and Section 508 tags |
| Best practices | axe-core best-practice tags |

Automated checks cover only machine-testable rules and do not certify WCAG or Section 508 conformance; manual and assistive-technology testing remains necessary.

### Phase 3 — GEO (Generative Engine Optimization)

Category: `geo`

| Check | What it detects |
| --- | --- |
| JSON-LD schema | Missing or incomplete structured data (Organization, WebPage, FAQPage, BreadcrumbList) |
| Content dates | No publication or modification dates in meta tags or `<time>` elements |
| FAQ sections | No FAQ markup, `<details>` elements, or "frequently asked" content |
| Question-format headings | Headings not written as questions (e.g. "Eligibility" vs. "Who qualifies?") |
| Page summaries | No TL;DR or summary section at top of content |
| Credibility links | No outbound links to authoritative sources (FDA, NIH, CMS) |
| Internal linking | Fewer than 3 internal cross-links on the page |
| Alt text quality | Images with non-descriptive alt text (generic names, file paths) |

### Phase 4 — UX & Performance

Category: `ux-performance`

| Check | What it detects |
| --- | --- |
| Image optimization | Images not in modern formats (WebP / AVIF) |
| Lazy loading | Below-fold images missing `loading="lazy"` |
| Responsive images | Images without `srcset` or `<picture>` element |
| Viewport meta | Missing `<meta name="viewport">` tag |
| Touch targets | Interactive elements smaller than 44 × 44 px (WCAG 2.5.8) |
| Long forms | Forms with more than 8 fields (drop-off risk) |
| Skip-to-content link | No skip link as first focusable element for keyboard users |

### Phase 5 — SEO & Discoverability

Category: `seo`

| Check | What it detects |
| --- | --- |
| Meta title | Missing or over-length `<title>` tag (> 60 chars) |
| Meta description | Missing or over-length meta description (> 160 chars) |
| Canonical URL | Missing `<link rel="canonical">` |
| Heading hierarchy | Missing H1, multiple H1s, or skipped heading levels |
| Open Graph tags | Missing `og:title` / `og:description` for social sharing |
| Twitter Card | Missing `twitter:card` meta tag |
| Lang attribute | Missing `lang` on `<html>` element |
| robots.txt | Missing file or no Sitemap directive |
| sitemap.xml | Missing XML sitemap |

### Phase 6 — Baseline & Measurement

Category: `baseline`

| Check | What it detects |
| --- | --- |
| Site inventory | Counts unique internal pages linked from the scanned page |
| Total issue summary | Aggregates issue count across all six phases |
| Migration planning | Lists discovered internal paths for redirect mapping |

> **Real-time progress:** The scan streams step-by-step progress via SSE. The frontend shows a live phase-by-phase log with animated indicators, so users see exactly what the engine is checking at each moment.

<a id="objective"></a>

## 17. Final Project Objective

AccessiAI should demonstrate that its developer can independently design, develop, test, and deploy a production-oriented full-stack web application.

**Frontend**Modern React development, advanced frontend architecture, accessible responsive UI.

**Backend**Python backend development, RESTful API design, GraphQL integration.

**Data & AI**Relational database design and AI API integration.

**Quality**Automated browser testing, WCAG implementation, security, testing, and deployment.

> **Primary portfolio objective:** Demonstrate Senior Frontend Developer capabilities while also showcasing practical full-stack development and AI engineering skills.

AccessiAI · Full-stack project specification · Built as a portfolio planning document
