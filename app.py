from flask import Flask, render_template, request, jsonify
import os
import re
import bcrypt
import hashlib
from pathlib import Path

app = Flask(__name__)

# Common weak passwords list
weak_passwords = ["password", "123456", "qwerty", "admin", "letmein"]

# Small bundled dictionary for the Vercel/serverless demo.
WORDLIST = Path(__file__).with_name("wordlist.txt")


# ------------ Password Strength Checker ------------
def password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter.")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Include at least one digit.")

    if re.search(r"[@$!%*?&]", password):
        score += 1
    else:
        feedback.append("Include at least one special character.")

    if password.lower() in weak_passwords:
        feedback.append("This is a very common password. Avoid it!")
        score = 1

    if score <= 2:
        strength = "Weak 🔴"
    elif score <= 4:
        strength = "Moderate 🟡"
    else:
        strength = "Strong 🟢"

    return strength, feedback


# ------------ Dictionary Hash Checker ------------
def crack_hash_file(target_hash, wordlist_path):
    """Stream a mounted password dictionary without loading it all into RAM."""
    target_hash = target_hash.strip().lower()

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                candidate = line.rstrip("\r\n")
                if not candidate:
                    continue

                # SHA-256 dictionary check
                if re.fullmatch(r"[0-9a-f]{64}", target_hash):
                    if hashlib.sha256(candidate.encode()).hexdigest() == target_hash:
                        return candidate, "SHA-256 match found."

                # bcrypt dictionary check
                elif target_hash.startswith(("$2a$", "$2b$", "$2y$")):
                    try:
                        if bcrypt.checkpw(candidate.encode(), target_hash.encode()):
                            return candidate, "Bcrypt match found."
                    except ValueError:
                        return None, "Invalid bcrypt hash."

                else:
                    return None, "Unsupported hash format. Enter a SHA-256 or bcrypt hash."
    except (FileNotFoundError, OSError):
        return None, "Cracking wordlist is unavailable on the backend."

    return None, "No match found in the configured dictionary."


def crack_hash_demo(target_hash):
    """Use the small bundled dictionary when no remote backend is configured."""
    return crack_hash_file(target_hash, WORDLIST)


# ------------ Remote Azure Cracking Backend ------------
def crack_hash_remote(target_hash):
    """Call an Azure-hosted cracking backend when CRACK_BACKEND_URL is configured."""
    import requests

    backend_url = os.getenv("CRACK_BACKEND_URL", "").rstrip("/")
    backend_key = os.getenv("CRACK_BACKEND_KEY", "")

    if not backend_url:
        return None, None

    if not backend_key:
        return None, "CRACK_BACKEND_KEY is not configured."

    try:
        response = requests.post(
            f"{backend_url}/crack",
            json={"hash": target_hash},
            headers={"X-Backend-Key": backend_key},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("password"), data.get("message", "No result.")
    except requests.RequestException:
        return None, "Cracking backend is temporarily unavailable."


# ------------ Azure Backend Endpoint ------------
@app.post("/crack")
def crack_endpoint():
    """Dictionary-check endpoint for the Azure worker/container."""
    expected_key = os.getenv("CRACK_BACKEND_KEY", "")
    supplied_key = request.headers.get("X-Backend-Key", "")

    if not expected_key or supplied_key != expected_key:
        return jsonify({"status": "error", "message": "Unauthorized backend request."}), 401

    data = request.get_json(silent=True) or {}
    target_hash = str(data.get("hash", "")).strip()

    if not re.fullmatch(r"[0-9a-fA-F]{64}", target_hash) and not target_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return jsonify({"status": "invalid", "message": "Enter a SHA-256 or bcrypt hash."}), 400

    wordlist_path = os.getenv("CRACKSTATION_WORDLIST_PATH", "/data/rockyou.txt")
    password, message = crack_hash_file(target_hash, wordlist_path)

    if password is not None:
        return jsonify({"status": "found", "password": password, "message": message})
    return jsonify({"status": "not_found", "password": None, "message": message})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


# ------------ Main Page ------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    feedback = []
    hash_result = None
    cracked_password = None
    crack_message = None

    if request.method == "POST":
        password = request.form.get("password", "")
        hash_input = request.form.get("hash_input", "").strip()

        if password:
            strength, feedback = password_strength(password)
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            bcrypt_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            result = strength
            hash_result = {"sha256": sha256_hash, "bcrypt": bcrypt_hash}

        elif hash_input:
            if os.getenv("CRACK_BACKEND_URL"):
                cracked_password, crack_message = crack_hash_remote(hash_input)
                if crack_message is None:
                    crack_message = "No match found."
            else:
                cracked_password, crack_message = crack_hash_demo(hash_input)

    return render_template(
        "index.html",
        result=result,
        feedback=feedback,
        hash_result=hash_result,
        cracked_password=cracked_password,
        crack_message=crack_message,
    )


if __name__ == "__main__":
    app.run(debug=True)
