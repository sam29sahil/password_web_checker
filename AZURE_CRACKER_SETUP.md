# Azure full-dictionary cracking backend

This project is designed so the public Vercel app can use an Azure-hosted backend for dictionary checks.

## Architecture

```text
Browser
  |
  v
Vercel Flask app
  |
  | POST /crack + X-Backend-Key
  v
Azure Container App / App Service (Docker)
  |
  | reads /data/rockyou.txt
  v
Azure Files mounted volume
```

The full CrackStation/rockyou-style dictionary should **not** be committed to GitHub or bundled into the Vercel deployment.

## Azure environment variables

Set these on the Azure backend:

```text
CRACK_BACKEND_KEY=<long-random-secret>
CRACKSTATION_WORDLIST_PATH=/data/rockyou.txt
PORT=8000
```

Set these on the Vercel frontend:

```text
CRACK_BACKEND_URL=https://<your-azure-backend-host>
CRACK_BACKEND_KEY=<same-long-random-secret>
```

Never put `CRACK_BACKEND_KEY` in frontend JavaScript or commit it to GitHub.

## Wordlist storage

1. Create an Azure Storage Account.
2. Create an Azure Files share.
3. Upload the dictionary as `rockyou.txt`.
4. Mount the Azure Files share in the container at `/data`.
5. Verify the container can read `/data/rockyou.txt`.

The application streams the file line-by-line rather than loading the entire dictionary into RAM.

## Container deployment

Build the repository Docker image using the included `Dockerfile` and deploy it as an Azure container workload. The container must expose HTTP port `8000` (or the value supplied through `PORT`).

After deployment, verify:

```text
GET https://<your-azure-backend-host>/health
```

Expected response:

```json
{"status":"ok"}
```

## Important limitation

A complete dictionary scan can take longer than a normal serverless HTTP request, especially for bcrypt because bcrypt is intentionally expensive. The current Vercel integration makes one synchronous HTTP request to Azure with a 30-second client timeout.

For a production-grade full CrackStation implementation, replace the synchronous `/crack` call with an asynchronous job system:

```text
Vercel -> POST /jobs -> Azure queue/worker -> dictionary scan
                         |
Vercel <- GET /jobs/<id> <- result
```

This avoids keeping a web request open while a large dictionary is scanned.

## Security notes

This feature is intended for authorized password-recovery/security-lab testing. Keep the Azure endpoint authenticated, add rate limiting before exposing it publicly, and avoid logging submitted hashes or recovered plaintext passwords.
