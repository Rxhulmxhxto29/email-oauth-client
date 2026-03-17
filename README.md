# Email OAuth Client

A production-style Flask web application that authenticates users via **Google OAuth 2.0** and displays the **latest 10 emails** from their Gmail inbox.

## Architecture

```
Browser  ──▶  Flask App  ──▶  Google OAuth 2.0  ──▶  Gmail API
                 │
                 ├── app.py             → Routes & request handling
                 ├── auth.py            → OAuth flow helpers
                 ├── gmail_service.py   → Gmail API communication
                 └── config.py          → Configuration & secrets
```

**Key design choices:**

| Concern | Approach |
|---|---|
| Auth flow | `google_auth_oauthlib.flow.Flow` (web-server flow) |
| Token storage | Encrypted Flask session (no database) |
| Secrets | Environment variables only |
| Gmail scope | `gmail.readonly` — read-only, no modification |

---

## Project Structure

```
email-oauth-client/
├── app.py                  # Flask routes
├── auth.py                 # OAuth 2.0 logic
├── gmail_service.py        # Gmail API calls
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
├── templates/
│   ├── index.html          # Login page
│   └── emails.html         # Inbox view
└── static/                 # (reserved for future assets)
```

---

## Prerequisites

- Python 3.10+
- A Google Cloud project with the **Gmail API** enabled
- OAuth 2.0 Client ID credentials (Web application type)

---

## Google Cloud & OAuth Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project → New Project**
3. Name it (e.g. `email-oauth-client`) and click **Create**

### 2. Enable the Gmail API

1. Navigate to **APIs & Services → Library**
2. Search for **Gmail API** and click **Enable**

### 3. Configure the OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **External** user type
3. Fill in the required fields:
   - App name, user support email, developer contact email
4. Under **Scopes**, add: `https://www.googleapis.com/auth/gmail.readonly`
5. Under **Test Users**, add any Google account(s) you want to test with
6. Click **Save and Continue**

### 4. Create OAuth Client ID

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth Client ID**
3. Application type: **Web application**
4. Add **Authorized redirect URIs**:
   - For local dev: `http://localhost:5000/oauth2callback`
   - For Render: `https://your-app-name.onrender.com/oauth2callback`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

---

## Local Development

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
# Linux/macOS
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export FLASK_SECRET_KEY="a-random-secret-string"

# Windows (PowerShell)
$env:GOOGLE_CLIENT_ID="your-client-id"
$env:GOOGLE_CLIENT_SECRET="your-client-secret"
$env:FLASK_SECRET_KEY="a-random-secret-string"
```

### 4. Run the application

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Deploying with Docker

### 1. Build the image

```bash
docker build -t email-oauth-client .
```

### 2. Run the container

```bash
docker run -p 5000:5000 \
  -e GOOGLE_CLIENT_ID="your-client-id" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret" \
  -e FLASK_SECRET_KEY="a-random-secret-string" \
  email-oauth-client
```

> **Note:** When deploying to production with Docker, remember to set `OAUTH_REDIRECT_URI` to your actual HTTPS domain callback (e.g. `https://yourdomain.com/oauth2callback`). `OAUTHLIB_INSECURE_TRANSPORT` will default to `0` securely.

---

## Deploying to Render (Free Tier)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-user/email-oauth-client.git
git push -u origin main
```

### 2. Create a Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Add Environment Variables in Render

| Variable | Value |
|---|---|
| `GOOGLE_CLIENT_ID` | Your OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Your OAuth client secret |
| `FLASK_SECRET_KEY` | A secure random string |
| `OAUTH_REDIRECT_URI` | `https://your-app-name.onrender.com/oauth2callback` |
| `OAUTHLIB_INSECURE_TRANSPORT` | `0` |

### 4. Update Google Cloud Console

Add `https://your-app-name.onrender.com/oauth2callback` as an **Authorized redirect URI** in your OAuth Client ID settings.

---

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page with Login button |
| `/login` | GET | Initiates Google OAuth redirect |
| `/oauth2callback` | GET | Handles OAuth callback |
| `/emails` | GET | Displays latest 10 inbox emails |
| `/logout` | GET | Clears session, redirects home |

---

## Security Notes

- **OAuth tokens are never exposed** — stored in server-side encrypted sessions
- **Secrets are never committed** — loaded from environment variables
- **`credentials.json` is git-ignored** — included in `.gitignore`
- **Read-only access** — only `gmail.readonly` scope is requested
- **CSRF protection** — OAuth state parameter validated during callback
- **HTTPS enforced** in production — `OAUTHLIB_INSECURE_TRANSPORT=0`

---

## License

MIT
