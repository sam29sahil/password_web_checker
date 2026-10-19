# Password Web Checker

A Flask-based cybersecurity learning project that demonstrates password-strength feedback, password hashing, and dictionary-based hash verification in a controlled lab.

**Live demo:** https://password-web-checker.vercel.app  
**Repository:** https://github.com/sam29sahil/password_web_checker

## Features

- Password-strength feedback based on length and character categories.
- Demonstrates SHA-256 hashing and bcrypt password hashing.
- Checks SHA-256 or bcrypt hashes against a configured dictionary file.
- Optional authenticated backend integration through environment variables.
- Health endpoint at `/health`.
- Flask application packaged for Vercel, with a Dockerfile for container-based deployment.

## Technology stack

- Python
- Flask
- bcrypt
- Requests
- HTML and CSS
- Vercel / Docker deployment configuration

## Run locally

Use Python 3.11 or 3.12 if possible.

```bash
git clone https://github.com/sam29sahil/password_web_checker.git
cd password_web_checker

python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Kali Linux / macOS**
```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Configuration

The optional remote dictionary backend uses server-side environment variables:

- `CRACK_BACKEND_URL`: base URL of the authorized backend.
- `CRACK_BACKEND_KEY`: shared secret used for backend authentication.
- `CRACKSTATION_WORDLIST_PATH`: path to the dictionary file on the backend (default: `/data/rockyou.txt`).

Do not commit secrets, real password lists, recovered passwords, or environment files to GitHub. Keep backend credentials in your hosting provider's secret/environment-variable settings. See [AZURE_CRACKER_SETUP.md](AZURE_CRACKER_SETUP.md) before enabling the optional backend.

## Security notes and limitations

- **Use only test passwords and hashes you own or are explicitly authorized to assess.**
- The strength score is a basic educational heuristic, not a guarantee of password security. It does not currently model all common patterns, breached-password lists, or password predictability.
- SHA-256 is shown for learning about hashes. It is a fast general-purpose hash and **must not be used alone for storing user passwords**. For real password storage, use a maintained password-hashing library and an appropriate algorithm such as Argon2id, scrypt, or bcrypt.
- bcrypt is demonstrated here, but this application is not an authentication system and does not currently store user accounts.
- Dictionary matching does not decrypt a hash. It hashes or verifies candidate passwords and checks whether a candidate matches.
- The optional dictionary endpoint can reveal a matching candidate. Do not expose it publicly without authorization controls, rate limiting, request limits, monitoring, and careful handling of sensitive values.
- Avoid submitting real or reused passwords to any public website, including this demo. Use generated test values only.
- This is an educational project, not a production-ready password manager or security assessment service.

## Project structure

```text
password_web_checker/
├── api/
│   └── index.py
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
├── Dockerfile
├── vercel.json
└── README.md
```

## Learning outcomes

This project demonstrates introductory concepts in Python web development, password-strength heuristics, cryptographic hashes, bcrypt, dictionary-based verification, environment-based configuration, and deployment.

## Responsible-use disclaimer

Use this tool only for educational testing and authorized password-recovery/security work. Do not use it to process credentials or hashes belonging to other people without permission.
