# Dev Care — API Endpoint Documentation

**Base URL:** `http://localhost:8000`
**Authentication:** JWT (via `Authorization: Bearer <access_token>`)

---

## 1. Authentication Endpoints (`/api/auth/`)

### 1.1 Register

| | |
|---|---|
| **URL** | `POST /api/auth/register/` |
| **Auth** | ❌ None |
| **Description** | Register a new user (patient or doctor). Returns JWT tokens immediately so the user is logged in on registration. |

**Request Body:**
```json
{
  "username": "Robert811",
  "email": "bhattarairobert@example.com",
  "password": "StrongPass123",
  "password_confirm": "StrongPass",
  "first_name": "Robert",
  "last_name": "Bhattarai",
  "role": "patient"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `username` | string | ✅ | Unique username |
| `email` | string | ✅ | Unique email |
| `password` | string | ✅ | Min 8 characters |
| `password_confirm` | string | ✅ | Must match `password` |
| `first_name` | string | ❌ | |
| `last_name` | string | ❌ | |
| `role` | string | ❌ | `"patient"` (default) or `"doctor"` |

**Success Response (`201 Created`):**
```json
{
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "username": "Robert811",
    "email": "bhattarairobert@example.com",
    "role": "patient"
  },
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Error Response (`400 Bad Request`):**
```json
{
  "password_confirm": ["Passwords do not match."],
  "email": ["Email is already in use."]
}
```

---

### 1.2 Login

| | |
|---|---|
| **URL** | `POST /api/auth/login/` |
| **Auth** | ❌ None |
| **Description** | Authenticate a user and return JWT tokens along with user info including role. |

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePass123"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `username` | string | ✅ | |
| `password` | string | ✅ | |

**Success Response (`200 OK`):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "patient"
  }
}
```

**Error Response (`401 Unauthorized`):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 1.3 Refresh Token

| | |
|---|---|
| **URL** | `POST /api/auth/refresh/` |
| **Auth** | ❌ None |
| **Description** | Get a new access token using a valid refresh token. |

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `refresh` | string | ✅ | A valid refresh token |

**Success Response (`200 OK`):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Error Response (`401 Unauthorized`):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```
---

## 3. AI Module Endpoints (`/api/ai/`)

> [!IMPORTANT]
> This is a legacy/utility endpoint. The primary rehab flow uses the `/api/rehab/` endpoints above.

### 3.1 Upload Session (Legacy)

| | |
|---|---|
| **URL** | `POST /api/ai/upload-session/` |
| **Auth** | ✅ Doctor or Patient |
| **Description** | Upload a standalone exercise session result. If called by a doctor, `patient_id` is required. If called by a patient, the session is automatically assigned to them. |

**Request Body (as Patient):**
```json
{
  "exercise": "bicep curl",
  "reps": 10,
  "avg_range": 130.5,
  "form_accuracy": 88.0,
  "duration": 45.0
}
```

**Request Body (as Doctor):**
```json
{
  "patient_id": 3,
  "exercise": "bicep curl",
  "reps": 10,
  "avg_range": 130.5,
  "form_accuracy": 88.0,
  "duration": 45.0
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `patient_id` | integer | Only for doctors | Must reference a patient user |
| `exercise` | string | ✅ | Exercise name (lowercased) |
| `reps` | integer | ✅ | ≥ 0 |
| `avg_range` | float | ✅ | Average range of motion (≥ 0) |
| `form_accuracy` | float | ✅ | 0.0–100.0 |
| `duration` | float | ✅ | Duration in seconds (≥ 0) |

**Success Response (`201 Created`):**
```json
{ "status": "saved" }
```

**Error Response (`400 Bad Request`):**
```json
{ "detail": "exercise is required." }
```

---

## Quick Reference

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/auth/register/` | ❌ | Any | Register a new user |
| `POST` | `/api/auth/login/` | ❌ | Any | Login and get JWT tokens |
| `POST` | `/api/auth/refresh/` | ❌ | Any | Refresh an access token |
| `POST` | `/api/ai/upload-session/` | ✅ | Doctor/Patient | Upload standalone session (legacy) |
