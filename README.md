# WebShield Scanner

**Web Security Scanner and Learning Mobile App**

WebShield Scanner is a cybersecurity learning and authorized penetration testing support application. It allows users to enter a website URL, scan it for common security weaknesses, and receive a structured security report with explanations, risk levels, and recommended fixes.

## Features

- 🔍 URL Scanner with authorization confirmation
- 🗺️ Attack Surface Mapping
- 🛡️ Security Header Checks (CSP, HSTS, X-Frame-Options, etc.)
- 🔒 SSL/TLS Validation
- 🍪 Cookie Security Checks
- 📁 Sensitive Data Exposure Detection
- 📦 Outdated Component Detection
- 🛡️ Safe Vulnerability Testing (SQLi, XSS, CSRF indicators)
- 📚 Learning Center with OWASP Top 10
- 📄 Report Generation (HTML, PDF, JSON)
- 💰 Premium Plan ($5 - Ad-free, Unlimited Scans, Advanced Features)

## Target Users

- Cybersecurity students
- Penetration testers
- Web developers
- Small business owners
- IT support teams
- Cybersecurity trainers

## Technology Stack

**Frontend (Mobile)**
- React
- Capacitor
- Bootstrap
- Three.js

**Backend**
- Python Flask
- PostgreSQL / SQLite
- BeautifulSoup
- Playwright / Selenium

**Infrastructure**
- Render / DigitalOcean / Railway / AWS
- Amazon Appstore
- Google AdMob
- Stripe / Amazon IAP

## Project Structure

# WebShield Scanner — Project Structure

# WebShield Scanner — Project Structure

## Overview

```
webshield-scanner/
├── backend/          # Flask backend application
├── mobile-wrapper/    # React + Capacitor mobile app
├── docs/              # Project documentation
└── scripts/           # Utility scripts
```

## Full Structure

```
webshield-scanner/
│
├── README.md
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── gunicorn.conf.py
├── Procfile
├── render.yaml
├── pyproject.toml
│
├── backend/
│   ├── run.py
│   ├── wsgi.py
│   ├── config.py
│   ├── extensions.py
│   ├── seed.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── scan.py
│   │   │   ├── finding.py
│   │   │   ├── subscription.py
│   │   │   ├── learning_lesson.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── page_routes.py
│   │   │   ├── auth_routes.py
│   │   │   ├── dashboard_routes.py
│   │   │   ├── scan_routes.py
│   │   │   ├── report_routes.py
│   │   │   ├── learning_routes.py
│   │   │   ├── subscription_routes.py
│   │   │   ├── settings_routes.py
│   │   │   └── admin_routes.py
│   │   │
│   │   ├── scanner/
│   │   │   ├── __init__.py
│   │   │   ├── url_validator.py
│   │   │   ├── crawler.py
│   │   │   ├── attack_surface.py
│   │   │   ├── headers.py
│   │   │   ├── ssl_check.py
│   │   │   ├── cookies.py
│   │   │   ├── forms.py
│   │   │   ├── sensitive_files.py
│   │   │   ├── component_check.py
│   │   │   ├── safe_vulnerability_checks.py
│   │   │   ├── score_engine.py
│   │   │   └── report_builder.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── scan_service.py
│   │   │   ├── report_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── ad_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── audit_service.py
│   │   │
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── decorators.py
│   │   │   ├── rate_limit.py
│   │   │   ├── csrf.py
│   │   │   ├── password.py
│   │   │   └── policy.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py
│   │   │   ├── validators.py
│   │   │   ├── constants.py
│   │   │   └── response.py
│   │   │
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── auth_base.html
│   │   │   │
│   │   │   ├── pages/
│   │   │   │   ├── splash.html
│   │   │   │   ├── dashboard.html
│   │   │   │   ├── new_scan.html
│   │   │   │   ├── scan_progress.html
│   │   │   │   ├── report_details.html
│   │   │   │   ├── attack_surface_map.html
│   │   │   │   ├── learning_center.html
│   │   │   │   ├── premium_upgrade.html
│   │   │   │   └── settings.html
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── login.html
│   │   │   │   ├── register.html
│   │   │   │   ├── forgot_password.html
│   │   │   │   └── reset_password.html
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   ├── report_pdf.html
│   │   │   │   └── report_print.html
│   │   │   │
│   │   │   ├── learning/
│   │   │   │   ├── lesson_details.html
│   │   │   │   └── demo_lab.html
│   │   │   │
│   │   │   └── partials/
│   │   │       ├── navbar.html
│   │   │       ├── bottom_nav.html
│   │   │       ├── sidebar.html
│   │   │       ├── flash_messages.html
│   │   │       ├── ad_banner.html
│   │   │       ├── premium_badge.html
│   │   │       └── scan_card.html
│   │   │
│   │   └── static/
│   │       ├── css/
│   │       │   ├── main.css
│   │       │   ├── auth.css
│   │       │   ├── dashboard.css
│   │       │   ├── scanner.css
│   │       │   ├── reports.css
│   │       │   ├── learning.css
│   │       │   └── mobile.css
│   │       │
│   │       ├── js/
│   │       │   ├── app.js
│   │       │   ├── auth.js
│   │       │   ├── dashboard.js
│   │       │   ├── new-scan.js
│   │       │   ├── scan-progress.js
│   │       │   ├── report-details.js
│   │       │   ├── attack-surface-map.js
│   │       │   ├── learning-center.js
│   │       │   ├── premium.js
│   │       │   ├── settings.js
│   │       │   ├── api.js
│   │       │   │
│   │       │   └── three/
│   │       │       ├── cyber-grid.js
│   │       │       ├── splash-animation.js
│   │       │       ├── scanner-animation.js
│   │       │       └── network-map.js
│   │       │
│   │       ├── images/
│   │       │   ├── logo.png
│   │       │   ├── shield.png
│   │       │   └── icons/
│   │       │
│   │       ├── uploads/
│   │       ├── reports/
│   │       └── vendor/
│   │           ├── bootstrap/
│   │           └── three/
│   │
│   ├── migrations/
│   ├── instance/
│   │   └── webshield.db
│   │
│   └── tests/
│       ├── test_auth.py
│       ├── test_scanner.py
│       ├── test_reports.py
│       ├── test_subscriptions.py
│       └── test_security.py
│
├── mobile-wrapper/
│   ├── package.json
│   ├── capacitor.config.ts
│   ├── vite.config.js
│   ├── index.html
│   │
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── config.js
│   │   │
│   │   ├── pages/
│   │   │   ├── Splash.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── NewScan.jsx
│   │   │   ├── ScanProgress.jsx
│   │   │   ├── ReportDetails.jsx
│   │   │   ├── AttackSurfaceMap.jsx
│   │   │   ├── LearningCenter.jsx
│   │   │   ├── PremiumUpgrade.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── BottomNav.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── ScanCard.jsx
│   │   │   ├── FindingCard.jsx
│   │   │   ├── ScoreRing.jsx
│   │   │   ├── AdBanner.jsx
│   │   │   └── PremiumBadge.jsx
│   │   │
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── authApi.js
│   │   │   ├── scanApi.js
│   │   │   ├── reportApi.js
│   │   │   └── paymentApi.js
│   │   │
│   │   ├── three/
│   │   │   ├── CyberGrid.jsx
│   │   │   ├── ScannerAnimation.jsx
│   │   │   └── NetworkMap.jsx
│   │   │
│   │   ├── styles/
│   │   │   ├── global.css
│   │   │   ├── mobile.css
│   │   │   └── theme.css
│   │   │
│   │   └── assets/
│   │       ├── logo.png
│   │       └── icons/
│   │
│   ├── android/
│   └── ios/
│
├── docs/
│   ├── project_documentation.md
│   ├── problem_definition.md
│   ├── objectives.md
│   ├── system_design.md
│   ├── database_design.md
│   ├── api_documentation.md
│   ├── test_plan.md
│   ├── deployment_guide.md
│   ├── amazon_appstore_guide.md
│   └── legal_policy.md
│
└── scripts/
    ├── create_db.py
    ├── seed_lessons.py
    ├── run_dev.sh
    ├── build_mobile.sh
    └── export_report_sample.py
```
text

## Quick Start

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/create_db.py

# Seed learning content
python backend/seed.py

# Run development server
python backend/run.py
Mobile App Setup
bash
cd mobile-wrapper
npm install

# Development
npm run dev

# Build for Android
npm run build:android

# Build for iOS
npm run build:ios
Deployment
Backend (Render)
Connect your GitHub repository to Render

Use the render.yaml configuration

Set environment variables in Render dashboard

Mobile App (Amazon Appstore)
Build APK/AAB: npm run build:android

Follow Amazon Appstore submission guidelines

Configure in-app purchases for premium plan

Ethical and Legal Policy
⚠️ IMPORTANT: This tool is for authorized testing only.

Only scan websites you own

Only scan websites where you have written permission

Do not use for illegal hacking

Do not use to attack, damage, or disrupt services

The app is for education, security testing, and defensive assessment only

License
This project is for educational and authorized security testing purposes only.

Contributing
Please read the contributing guidelines before submitting pull requests.

Support
For support, please open an issue on GitHub or contact the development team.

Made with ❤️ for cybersecurity education
