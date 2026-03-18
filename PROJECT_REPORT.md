# Email OAuth Client — Project Report

**Project Name:** Email OAuth Client
**Author:** Rahul Mahato
**Live URL:** [https://email-oauth-client.onrender.com](https://email-oauth-client.onrender.com)
**GitHub:** [https://github.com/Rxhulmxhxto29/email-oauth-client](https://github.com/Rxhulmxhxto29/email-oauth-client)
**Date:** March 18, 2026

---

## Table of Contents

1. [What is This Project?](#1-what-is-this-project)
2. [What Does This Project Do?](#2-what-does-this-project-do)
3. [What Problem Does It Solve?](#3-what-problem-does-it-solve)
4. [How Does This Project Work?](#4-how-does-this-project-work)
5. [The Logic Behind the Project](#5-the-logic-behind-the-project)
6. [The Role of OAuth 2.0](#6-the-role-of-oauth-20)
7. [Technology Stack](#7-technology-stack)
8. [Application Flow Diagram](#8-application-flow-diagram)
9. [Architecture Diagram](#9-architecture-diagram)
10. [Project File Structure](#10-project-file-structure)
11. [Security Considerations](#11-security-considerations)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Conclusion](#13-conclusion)

---

## 1. What is This Project?

The **Email OAuth Client** is a web-based email client application built using Python and the Flask web framework. It allows users to securely log in with their Google account and view the latest 10 emails from their Gmail inbox — all without ever sharing their Google password with the application.

The application uses **OAuth 2.0** (Open Authorization), which is the industry-standard protocol used by Google, Facebook, GitHub, and virtually every major technology company to allow third-party applications to access user data safely.

In simple terms, think of it like this: instead of giving your house key to a stranger, you open the door yourself and allow them to look inside — but they cannot touch or take anything. That is exactly what this application does with your Gmail inbox.

---

## 2. What Does This Project Do?

The application performs the following core functions:

| Feature | Description |
|---|---|
| **Google Sign-In** | Users click a "Login with Google" button and are redirected to Google's official login page. The application never sees or stores the user's password. |
| **Fetch 10 Latest Emails** | After login, the application uses the Gmail API to retrieve the 10 most recent emails from the user's inbox. |
| **Display Email Details** | For each email, the application displays the **Sender**, **Subject Line**, **Date**, and a short **Preview Snippet** of the email body. |
| **Smart Categorization** | Each email is automatically assigned a category (Important, Work/Jobs, Social, Notifications, Promotions, or Other) based on the sender and subject line. |
| **Search & Filter** | A search bar allows users to filter their emails using keywords or Gmail search operators (e.g., `from:linkedin`, `subject:invoice`). |
| **Secure Logout** | Users can log out at any time, which completely clears their session data from the server. |

---

## 3. What Problem Does It Solve?

### The Problem

When developers or students need to build an application that reads emails, they face a significant challenge: **how do you access a user's email without asking for their password?**

Traditionally, email clients required users to enter their username and password directly into the application. This approach has several serious problems:

1. **Security Risk:** If the application is compromised, the attacker now has the user's password.
2. **Trust Issue:** Users are understandably reluctant to type their password into an unknown application.
3. **No Granular Control:** Once you give your password, the application can do anything — read, send, delete emails — with no restrictions.

### The Solution

This project solves all three problems by implementing **OAuth 2.0**:

1. **No password is ever shared.** The user logs in directly on Google's own website.
2. **Trust is established through Google.** Users see Google's familiar login page, not a random form.
3. **Granular permissions.** The application only requests `gmail.readonly` access — it can read emails but **cannot** send, modify, or delete anything.

---

## 4. How Does This Project Work?

Here is a step-by-step walkthrough of exactly what happens when a user uses the application:

### Step 1: User Visits the Application
The user opens `https://email-oauth-client.onrender.com` in their browser. They see a clean, dark-themed login page with a "Login with Google" button.

### Step 2: User Clicks "Login with Google"
The application generates a special URL that points to Google's OAuth consent screen. This URL contains:
- The application's **Client ID** (a unique identifier registered with Google).
- The **scope** (`gmail.readonly`) — telling Google exactly what permission is being requested.
- A **redirect URI** — the URL where Google should send the user back after login.
- A **state token** — a random string to prevent forgery attacks (CSRF protection).

### Step 3: User Logs In on Google's Website
The user is now on Google's official website (accounts.google.com). They enter their Google email and password directly on Google's page. The application never sees this information.

### Step 4: User Grants Permission
Google shows the user a consent screen explaining that "Email OAuth Client wants to view your Gmail messages." The user clicks "Allow."

### Step 5: Google Sends Back an Authorization Code
Google redirects the user back to the application's callback URL (`/oauth2callback`) with a temporary **authorization code** in the URL.

### Step 6: Application Exchanges the Code for an Access Token
The application's backend (Python server) takes this authorization code and sends it directly to Google's token server along with the application's **Client Secret** (a private password only the server knows). Google verifies everything and responds with an **Access Token**.

### Step 7: Application Fetches Emails Using the Access Token
The application uses this Access Token to make an authorized request to the Gmail API. It asks for the 10 most recent emails in the user's inbox. The Gmail API returns the email data.

### Step 8: Emails Are Displayed
The application processes the raw email data, categorizes each email, and renders a beautiful inbox page showing all 10 emails with their sender, subject, date, preview, and category badge.

---

## 5. The Logic Behind the Project

### File-by-File Breakdown

The project is organized into clearly separated modules, each handling one specific responsibility:

#### `config.py` — Configuration Manager
This file loads all sensitive information (Client ID, Client Secret, Flask Secret Key) from **environment variables**. It never hardcodes secrets. It also defines the Gmail API scope (`gmail.readonly`) and the OAuth redirect URI.

#### `auth.py` — OAuth Authentication Engine
This file contains the core OAuth logic:
- `get_auth_flow()` — Creates a Google OAuth Flow object configured with the application's credentials.
- `get_authorization_url()` — Generates the Google consent screen URL with the correct parameters.
- `exchange_code_for_credentials()` — Takes the temporary authorization code from Google and exchanges it for a permanent Access Token.
- `credentials_to_session()` / `credentials_from_session()` — Converts OAuth credentials to/from a format that can be stored in Flask's encrypted session cookie.

#### `gmail_service.py` — Gmail API Communication
This file handles all communication with Google's Gmail API:
- `get_gmail_service()` — Builds an authorized Gmail API service object using the user's Access Token.
- `fetch_latest_emails()` — Uses **HTTP Batch Requests** (a performance optimization) to fetch all 10 emails in a single network round-trip instead of making 10 separate requests. Each email is then passed through the categorizer.

#### `utils/email_classifier.py` — Smart Email Categorizer
This file contains a keyword-based classification engine that assigns each email to one of six categories:

| Category | Detection Logic |
|---|---|
| **Important** | Subject or sender contains: "security", "alert", "verification", "password" |
| **Work / Jobs** | Subject contains job-related keywords, or sender is Indeed, LinkedIn, Glassdoor |
| **Social** | Sender domain is linkedin.com, twitter.com, facebook.com, or instagram.com |
| **Notifications** | Subject contains: "notification", "update", "activity" |
| **Promotions** | Subject contains: "sale", "offer", "discount", "deal", "promotion" |
| **Other** | Default category if no keywords match |

#### `app.py` — Flask Web Server (The Central Hub)
This is the main application file that ties everything together. It defines five routes:

| Route | Purpose |
|---|---|
| `GET /` | Renders the login page |
| `GET /login` | Redirects the user to Google's OAuth consent screen |
| `GET /oauth2callback` | Handles Google's redirect after user grants permission |
| `GET /emails` | Fetches and displays the user's 10 latest emails |
| `GET /logout` | Clears the session and redirects to the home page |

---

## 6. The Role of OAuth 2.0

### What is OAuth 2.0?

**OAuth 2.0** (Open Authorization 2.0) is an industry-standard authorization framework. It allows a third-party application to obtain limited access to a user's account on another service (like Google, Facebook, or GitHub) **without the user ever revealing their password** to the third-party application.

### How OAuth 2.0 Works in This Project

There are **four participants** in the OAuth flow:

| Participant | Role in This Project |
|---|---|
| **Resource Owner** | The user (you) who owns the Gmail account |
| **Client** | The Email OAuth Client application (our Flask app) |
| **Authorization Server** | Google's OAuth server (accounts.google.com) |
| **Resource Server** | Gmail API (googleapis.com) |

### The OAuth 2.0 Flow (Authorization Code Grant)

This project uses the **Authorization Code Grant** flow, which is the most secure OAuth flow for web applications:

1. **Client → Authorization Server:** "I am app X, and I want to read this user's Gmail."
2. **Authorization Server → User:** "App X wants to read your Gmail. Do you allow this?"
3. **User → Authorization Server:** "Yes, I allow it."
4. **Authorization Server → Client:** "Here is a temporary authorization code."
5. **Client → Authorization Server:** "Here is the code + my secret password. Give me an Access Token."
6. **Authorization Server → Client:** "Verified. Here is your Access Token."
7. **Client → Resource Server:** "Here is my Access Token. Give me the user's emails."
8. **Resource Server → Client:** "Token is valid. Here are the 10 latest emails."

### Why OAuth 2.0 is Important

| Without OAuth | With OAuth |
|---|---|
| User gives password to the app | User logs in only on Google's page |
| App has full account access | App only gets `gmail.readonly` permission |
| If app is hacked, password is exposed | If app is hacked, only a temporary token is exposed |
| User cannot revoke access easily | User can revoke access anytime from Google Settings |

### The Scope: `gmail.readonly`

The application only requests the `gmail.readonly` scope. This means:
- ✅ Can read email messages
- ✅ Can list emails in the inbox
- ❌ Cannot send emails
- ❌ Cannot delete emails
- ❌ Cannot modify labels or settings
- ❌ Cannot access Google Drive, Calendar, or any other Google service

---

## 7. Technology Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Core programming language |
| **Flask** | 3.1.0 | Lightweight web framework for routing, sessions, and templating |
| **google-api-python-client** | 2.166.0 | Official Google API client library for accessing Gmail API |
| **google-auth** | 2.38.0 | Google's authentication library for handling OAuth tokens |
| **google-auth-oauthlib** | 1.2.1 | Higher-level OAuth 2.0 flow implementation for Google services |
| **google-auth-httplib2** | 0.2.0 | HTTP transport adapter for Google authentication |
| **Gunicorn** | 23.0.0 | Production-grade WSGI HTTP server (replaces Flask's dev server) |
| **python-dotenv** | 1.0.1 | Loads environment variables from `.env` files for local development |
| **Werkzeug (ProxyFix)** | Bundled with Flask | Middleware to correctly handle HTTPS behind reverse proxies |

### Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Page structure and semantic markup |
| **CSS3 (Vanilla)** | Complete styling with CSS Variables, gradients, and animations |
| **Jinja2** | Flask's built-in template engine for server-side rendering |
| **Google Fonts (Inter)** | Modern, professional typography |
| **SVG Icons** | Inline vector icons for buttons and UI elements |

### DevOps & Deployment

| Technology | Purpose |
|---|---|
| **Docker** | Containerization for consistent deployment across any environment |
| **Render** | Cloud Platform-as-a-Service (PaaS) for free hosting |
| **Git / GitHub** | Version control and source code management |
| **Gunicorn** | Production WSGI server (used in Docker and Render) |

### External Services

| Service | Purpose |
|---|---|
| **Google Cloud Console** | OAuth 2.0 Client ID and Secret management |
| **Gmail API** | RESTful API for reading email messages |
| **Google OAuth 2.0 Server** | Authorization and token exchange endpoint |

---

## 8. Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION FLOW DIAGRAM                        │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────┐                                                       
    │   USER   │                                                       
    └────┬─────┘                                                       
         │                                                             
         │  1. Opens https://email-oauth-client.onrender.com           
         ▼                                                             
    ┌──────────┐                                                       
    │  / route │──────────▶  Renders Login Page (index.html)           
    └────┬─────┘                                                       
         │                                                             
         │  2. Clicks "Login with Google"                              
         ▼                                                             
    ┌────────────┐                                                     
    │ /login     │──────────▶  Generates Google OAuth URL              
    │ route      │             (includes Client ID + scope + state)     
    └────┬───────┘                                                     
         │                                                             
         │  3. Redirect to Google                                      
         ▼                                                             
    ┌──────────────────┐                                               
    │  GOOGLE OAUTH    │                                               
    │  CONSENT SCREEN  │──────▶  User enters Google credentials        
    │  (Google's site) │         User clicks "Allow"                   
    └────┬─────────────┘                                               
         │                                                             
         │  4. Google redirects back with authorization code            
         ▼                                                             
    ┌────────────────┐                                                 
    │ /oauth2callback│──────────▶  Exchanges code for Access Token     
    │ route          │             (server-to-server, secret included)  
    └────┬───────────┘                                                 
         │                                                             
         │  5. Redirect to /emails                                     
         ▼                                                             
    ┌────────────┐                                                     
    │ /emails    │──────────▶  Uses Access Token to call Gmail API     
    │ route      │             Fetches 10 latest emails                
    │            │             Categorizes each email                   
    │            │             Renders inbox page (emails.html)         
    └────┬───────┘                                                     
         │                                                             
         │  6. User clicks "Logout"                                    
         ▼                                                             
    ┌────────────┐                                                     
    │ /logout    │──────────▶  Clears session data                     
    │ route      │             Redirects to login page                  
    └────────────┘                                                     
```

---

## 9. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SYSTEM ARCHITECTURE DIAGRAM                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────────────────────────────┐
│                 │         │           FLASK APPLICATION             │
│    USER'S       │  HTTPS  │                                         │
│    BROWSER      │◄───────►│  ┌─────────┐    ┌────────────────────┐  │
│                 │         │  │ app.py  │    │    auth.py          │  │
│  - index.html   │         │  │ (Routes)│───►│ (OAuth Flow)       │  │
│  - emails.html  │         │  └────┬────┘    └────────┬───────────┘  │
│  - styles.css   │         │       │                  │              │
│                 │         │       ▼                  │              │
└─────────────────┘         │  ┌────────────────┐     │              │
                            │  │gmail_service.py│     │              │
                            │  │(Gmail API)     │     │              │
                            │  └──────┬─────────┘     │              │
                            │         │               │              │
                            │         ▼               │              │
                            │  ┌────────────────┐     │              │
                            │  │email_classifier│     │              │
                            │  │(Categorization)│     │              │
                            │  └────────────────┘     │              │
                            │         │               │              │
                            │  ┌──────┴───────┐       │              │
                            │  │  config.py   │       │              │
                            │  │ (Env Vars)   │       │              │
                            │  └──────────────┘       │              │
                            └─────────┬───────────────┴──────────────┘
                                      │               │
                               HTTPS  │               │ HTTPS
                                      ▼               ▼
                            ┌─────────────┐  ┌────────────────────┐
                            │  GMAIL API  │  │  GOOGLE OAUTH 2.0  │
                            │  (Google)   │  │  SERVER (Google)    │
                            │             │  │                    │
                            │ Provides    │  │ Handles login,     │
                            │ email data  │  │ consent, and       │
                            │             │  │ token exchange     │
                            └─────────────┘  └────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT INFRASTRUCTURE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   GitHub Repository                     Render (Cloud PaaS)         │
│   ┌────────────────┐     Auto-Deploy    ┌────────────────────┐      │
│   │Source Code     │───────────────────►│ Docker Container   │      │
│   │(main branch)   │                    │ ┌────────────────┐ │      │
│   └────────────────┘                    │ │  Gunicorn      │ │      │
│                                         │ │  (WSGI Server) │ │      │
│                                         │ │       │        │ │      │
│                                         │ │  Flask App     │ │      │
│                                         │ └────────────────┘ │      │
│                                         │ Port: 10000        │      │
│                                         └────────────────────┘      │
│                                         URL: email-oauth-client     │
│                                              .onrender.com          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Project File Structure

```
email-oauth-client/
├── app.py                    # Main Flask application (routes & request handling)
├── auth.py                   # OAuth 2.0 flow (consent URL, token exchange)
├── config.py                 # Configuration & secrets (environment variables)
├── gmail_service.py          # Gmail API communication (batch email fetching)
├── utils/
│   ├── __init__.py           # Python package initializer
│   └── email_classifier.py  # Keyword-based email categorization engine
├── templates/
│   ├── index.html            # Login page template
│   └── emails.html           # Inbox/email list page template
├── static/
│   └── styles.css            # Complete dark-theme CSS (580 lines)
├── requirements.txt          # Python dependencies (pinned versions)
├── Dockerfile                # Docker container configuration
├── Procfile                  # PaaS deployment command (Gunicorn)
├── .dockerignore             # Files excluded from Docker image
├── .gitignore                # Files excluded from Git tracking
├── .env.example              # Template for environment variables
├── start.bat                 # One-click local execution script (Windows)
└── README.md                 # Full project documentation
```

---

## 11. Security Considerations

This project was designed with security as a top priority:

| Security Measure | Implementation |
|---|---|
| **No password storage** | OAuth 2.0 ensures the app never sees user passwords |
| **Read-only scope** | Only `gmail.readonly` — cannot send, delete, or modify emails |
| **Environment variables** | All secrets (Client ID, Secret, Flask Key) stored as env vars, never in code |
| **HTTPS enforcement** | `ProxyFix` middleware ensures secure HTTPS behind Render's load balancer |
| **CSRF protection** | OAuth `state` parameter prevents Cross-Site Request Forgery attacks |
| **Session encryption** | Flask sessions are cryptographically signed with a secret key |
| **No database** | No persistent storage of user data; everything lives in the session cookie |
| **Token expiry** | Access tokens automatically expire; the app handles re-authentication |

---

## 12. Deployment Architecture

The application is deployed using a fully automated CI/CD pipeline:

1. **Developer pushes code** to the `main` branch on GitHub.
2. **Render detects the push** automatically via webhook.
3. **Render builds a Docker image** using the project's `Dockerfile`.
4. **The Docker container starts** with Gunicorn serving the Flask app.
5. **The application goes live** at `https://email-oauth-client.onrender.com`.

Environment variables (Client ID, Client Secret, Flask Secret Key) are securely configured through Render's dashboard and injected into the container at runtime.

---

## 13. Conclusion

The **Email OAuth Client** is a fully functional, production-deployed web application that demonstrates a complete implementation of the OAuth 2.0 Authorization Code Grant flow. It successfully:

- ✅ Authenticates users through Google's official OAuth 2.0 service
- ✅ Retrieves the 10 latest emails from the user's Gmail inbox
- ✅ Displays emails with sender, subject, date, and preview information
- ✅ Categorizes emails intelligently using keyword-based classification
- ✅ Provides search and filter capabilities using Gmail search operators
- ✅ Runs securely in production with HTTPS, encrypted sessions, and read-only Gmail access
- ✅ Is deployed live and accessible at [https://email-oauth-client.onrender.com](https://email-oauth-client.onrender.com)

The project serves as a comprehensive example of how modern web applications can safely interact with third-party APIs using OAuth 2.0, without ever compromising user security.

---

*Report generated on March 18, 2026*
*Email OAuth Client v1.0 — by Rahul Mahato*
