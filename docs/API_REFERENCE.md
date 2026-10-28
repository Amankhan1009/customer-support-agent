# REST API Reference Specification

The **Customer Support Agent API** is built with **FastAPI**, featuring automatic OpenAPI schema generation, typed Pydantic validation, and JWT token authentication.

- **Base URL (Local)**: `http://localhost:8000`
- **Base URL (Production)**: `https://customer-support-agent-4960.onrender.com`
- **Interactive Swagger UI**: `/docs`
- **ReDoc UI**: `/redoc`

---

## 1. Authentication & Security

All `/support` endpoints require a valid JSON Web Token (JWT) passed in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Tokens are signed using `HS256` with a configurable secret key (`JWT_SECRET_KEY`) and default expiry of 60 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## 2. Health & Keepalive Endpoint

### `GET /health`
Health check endpoint used by Render free-tier keepalive and the Streamlit frontend wake-up probe.

#### Response (`200 OK`)
```json
{
  "status": "healthy"
}
```

---

## 3. Authentication Endpoints

### `POST /auth/register`
Creates a new user record with a salted bcrypt password hash and returns an access token.

#### Request Body
```json
{
  "username": "aman",
  "password": "MySecurePassword123"
}
```

#### Response (`201 Created`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Error Responses
- `400 Bad Request`: Username already registered.

---

### `POST /auth/login`
Authenticates existing credentials against the bcrypt hash and returns an access token.

#### Request Body
```json
{
  "username": "aman",
  "password": "MySecurePassword123"
}
```

#### Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid username or password.

---

## 4. Support Conversation Endpoints

### `POST /support`
Submits a customer message to be processed by the LangGraph engine for a specific conversation thread.

#### Headers
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "thread_id": "customer-aman-01",
  "message": "My return is for item #REF-99214. What is its status?"
}
```

#### Response A: Completed Execution (`200 OK`)
```json
{
  "thread_id": "customer-aman-01",
  "status": "completed",
  "response": "The item number for your return is #REF-99214. Your return status is currently under review.",
  "interrupt_data": null
}
```

#### Response B: Human Review Required (`200 OK`)
When sensitive signals (fraud, unauthorized charges, compromised accounts) are detected:
```json
{
  "thread_id": "customer-aman-01",
  "status": "human_review_required",
  "response": null,
  "interrupt_data": {
    "type": "human_support_review",
    "customer_message": "My account was compromised and I see an unauthorized charge of $450.",
    "intent": "billing",
    "escalation_reason": "sensitive_request",
    "diagnostic_result": null
  }
}
```

#### Error Responses
- `409 Conflict`: The conversation thread is currently waiting for human review. Call `/support/resume` before sending another message.

---

### `GET /support/threads`
Lists all conversation threads associated with the authenticated user.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Response (`200 OK`)
```json
[
  {
    "thread_id": "customer-aman-01",
    "title": "My return is for item #REF-99214..."
  },
  {
    "thread_id": "customer-aman-02",
    "title": "What features are in Pro tier?..."
  }
]
```

---

### `GET /support/{thread_id}`
Fetches the current state and status of a specific thread.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Response (`200 OK`)
```json
{
  "thread_id": "customer-aman-01",
  "status": "completed",
  "response": "The item number for your return is #REF-99214.",
  "interrupt_data": null
}
```

#### Error Responses
- `404 Not Found`: Thread ID does not exist in the checkpointer.

---

### `GET /support/{thread_id}/history`
Fetches chronological conversation history formatted for UI replay, including active interrupt status.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Response (`200 OK`)
```json
{
  "thread_id": "customer-aman-01",
  "messages": [
    {
      "role": "user",
      "content": "My return is for item #REF-99214. What is its status?"
    },
    {
      "role": "assistant",
      "content": "The item number for your return is #REF-99214. Your return status is currently under review."
    }
  ],
  "waiting_for_human": false,
  "interrupt_data": null
}
```

---

### `POST /support/resume`
Resumes an interrupted workflow waiting for human review.

#### Headers
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "thread_id": "customer-aman-01",
  "human_response": "We have reviewed your unauthorized charge and issued a full refund of $450. Your account has been secured."
}
```

#### Response (`200 OK`)
```json
{
  "thread_id": "customer-aman-01",
  "status": "completed",
  "response": "We have reviewed your unauthorized charge and issued a full refund of $450. Your account has been secured.",
  "interrupt_data": null
}
```

#### Error Responses
- `404 Not Found`: Conversation thread not found.
- `409 Conflict`: The conversation is not waiting for human review.
