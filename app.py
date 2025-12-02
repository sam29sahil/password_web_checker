from flask import Flask, render_template, request
import re, bcrypt, hashlib

app = Flask(__name__)

# Common weak passwords list
weak_passwords = ["password", "123456", "qwerty", "admin", "letmein"]

# ------------ Password Strength Checker ------------
def password_strength(password):
    score = 0
    feedback = []

    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long.")

    # Uppercase check
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter.")

    # Lowercase check
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter.")

    # Number check
    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Include at least one digit.")

    # Special character check
    if re.search(r"[@$!%*?&]", password):
        score += 1
    else:
        feedback.append("Include at least one special character.")

    # Weak password list check
    if password.lower() in weak_passwords:
        feedback.append("This is a very common password. Avoid it!")
        score = 1

    # Strength level
    if score <= 2:
        strength = "Weak 🔴"
    elif score == 3 or score == 4:
        strength = "Moderate 🟡"
    else:
        strength = "Strong 🟢"

    return strength, feedback


# ------------ Hash Cracker (Dictionary Attack) ------------
def crack_hash(target_hash, wordlist="/usr/share/wordlists/rockyou.txt"):
    try:
        with open(wordlist, "r", encoding="latin-1") as f:
            for word in f:
                word = word.strip()
                # Compare SHA256 hashes
                if hashlib.sha256(word.encode()).hexdigest() == target_hash:
                    return word
    except FileNotFoundError:
        return "⚠️ Wordlist not found (rockyou.txt missing)."
    return None


# ------------ Flask Routes ------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    feedback = []
    hash_result = None
    cracked_password = None

    if request.method == "POST":
        password = request.form.get("password")
        hash_input = request.form.get("hash_input")

        if password:
            # Password → Strength + Hash
            strength, feedback = password_strength(password)
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            bcrypt_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            result = strength
            hash_result = {"sha256": sha256_hash, "bcrypt": bcrypt_hash}

        elif hash_input:
            # Hash → Crack attempt
            cracked_password = crack_hash(hash_input)

    return render_template("index.html",
                           result=result,
                           feedback=feedback,
                           hash_result=hash_result,
                           cracked_password=cracked_password)


# ------------ Run App ------------
if __name__ == "__main__":
    app.run(debug=True)

