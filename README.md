Tech House | Secure Hardware Ecommerce
IKB 21503: Secure Software Development Project
1. Project Description
Tech House is a secure e-commerce web application developed using the Django framework. It provides a platform for users to browse PC hardware, manage a shopping cart, and maintain a secure user profile. The system is built with a security-first architecture, implementing specific countermeasures to align with OWASP Top 10 and ASVS standards.

2. Security Features Summary
This application implements the following mandatory security requirements:

Input Validation : Uses Django ORM for parameterized queries to prevent SQL Injection and Regex whitelisting to validate all user-supplied data.

Authentication & Lockout : Features a database-backed login tracker that triggers an account-specific lockout after 5 failed attempts, preventing brute-force attacks.

Role-Based Access Control : Enforces strict RBAC for Administrator, Staff, and Normal User roles across all endpoints using decorators and mixins.

Error Handling : Custom 404 and 500 error pages are implemented to prevent technical stack traces from leaking system architecture.

Logging & Monitoring : Automated signals capture administrative actions and suspicious security events (e.g., unauthorized access attempts) in a dedicated Audit Log.

Output Encoding & CSP : Utilizes Django's auto-escaping template engine to neutralize Cross-Site Scripting (XSS), reinforced by a Custom Content Security Policy (CSP) Middleware that strictly controls asset loading.

Configuration Security : Sensitive credentials are kept out of version control via .env files and .gitignore.

Supply Chain Security : All dependencies are pinned and verified using automated SCA tools (pip-audit).

3. Installation & Setup
To install and run this project locally, follow these steps to restore the secure environment:

3.1 Clone the Repository

Bash
git clone https://github.com/Frisc765056/Secure-Tech-House-Ecommerce-IKB21503.git
cd Secure-Tech-House-Ecommerce-IKB21503

3.2 Restore Security Credentials (.env) The project uses environment variables to protect secrets.

Locate .env.example in the root directory.

Duplicate it and rename the copy to .env.

Open .env and ensure DEBUG=True (for testing) and a SECRET_KEY are defined.

3.3 Create Virtual Environment & Install Dependencies

Bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

3.4 Initialize Database & Static Assets Since the production database and static files are ignored by Git for security, you must initialize them locally:

Bash
# Initialize the database schema
python manage.py migrate

# Restore Admin UI styling and project assets
python manage.py collectstatic

3.5 Create Administrative Account

Bash
python manage.py createsuperuser
4. How to Run
Start the development server with the following command:

Bash
python manage.py runserver
The application will be accessible at http://127.0.0.1:8000/.

5. Software Component Analysis (SCA)
All third-party libraries listed in requirements.txt have been verified for security vulnerabilities.

Dependency Scanning: Conducted via pip-audit -r requirements.txt.

SCA Result: The automated scan confirmed that no known vulnerabilities were found in the project's dependencies.

6. System Screenshots
User Profile & RBAC: Displays the profile for Staff1 with the Staff Member badge, proving authorization levels.

screenshots/RBAC.png

Account Lockout Trigger: Shows a triggered SECURITY LOCKOUT after 5 failed attempts, demonstrating brute-force defense.

screenshots/ACCOUNT LOCKOUT PROTECTION.png

Administrative Audit Logs: Displays the Audit Log capturing an ACCESS DENIED event for unauthorized users.

screenshots/SYSTEM AUDIT LOGS.png

Secure Error Handling: Displays the custom 500 System Malfunction page, masking technical stack traces.

screenshots/SECURE ERROR HANDLING.png

Software Component Analysis: Proves all dependencies are secure.

screenshots/SOFTWARE COMPONENT ANALYSIS.png