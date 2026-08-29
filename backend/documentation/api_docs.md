# EduManage API Documentation

Complete specification of API endpoints, authentication standards, request schemas, response schemas, and example JSON payloads for the **EduManage API Backend**.

---

## Table of Contents

1. [Global Architecture & Security](#1-global-architecture--security)
2. [Authentication & Account Management](#2-authentication--account-management)
   - [User Registration (`POST /auth/signup`)](#user-registration-post-authsignup)
   - [User Login (`POST /auth/login`)](#user-login-post-authlogin)
   - [OAuth2 Form Login (`POST /token`)](#oauth2-form-login-post-token)
3. [User Profile & Discovery](#3-user-profile--discovery)
   - [Authenticated User Profile (`GET /users/me`)](#authenticated-user-profile-get-usersme)
   - [User Search (`GET /users/search`)](#user-search-get-userssearch)
4. [Digital Wallet & Money Movement](#4-digital-wallet--money-movement)
   - [Wallet Dashboard (`GET /wallet/dashboard`)](#wallet-dashboard-get-walletdashboard)
   - [Send Money Transfer (`POST /wallet/transfer`)](#send-money-transfer-post-wallettransfer)
   - [Transaction History (`GET /wallet/transactions`)](#transaction-history-get-wallettransactions)
   - [Single Transaction Details (`GET /wallet/transactions/{reference_id}`)](#single-transaction-details-get-wallettransactionsreference_id)
   - [Double-Entry Ledger Audit Trail (`GET /wallet/ledger`)](#double-entry-ledger-audit-trail-get-walletledger)
5. [Money Requests](#5-money-requests)
   - [Create Money Request (`POST /wallet/request-money`)](#create-money-request-post-walletrequest-money)
   - [Incoming Money Requests (`GET /wallet/requests/incoming`)](#incoming-money-requests-get-walletrequestsincoming)
   - [Outgoing Money Requests (`GET /wallet/requests/outgoing`)](#outgoing-money-requests-get-walletrequestsoutgoing)
   - [Accept / Decline Request (`POST /wallet/request-money/{request_id}/action`)](#accept--decline-request-post-walletrequest-moneyrequest_idaction)
6. [In-App Notifications](#6-in-app-notifications)
   - [Get Notifications (`GET /notifications`)](#get-notifications-get-notifications)
   - [Mark Single Notification Read (`PATCH /notifications/{notification_id}/read`)](#mark-single-notification-read-patch-notificationsnotification_idread)
   - [Mark All Notifications Read (`PATCH /notifications/read-all`)](#mark-all-notifications-read-patch-notificationsread-all)
7. [System Observability & Health](#7-system-observability--health)
   - [Health Status Check (`GET /health`)](#health-status-check-get-health)
8. [AI Chat & SSE Streaming](#8-ai-chat--sse-streaming)
   - [Streaming Chat Response (`POST /chat`)](#streaming-chat-response-post-chat)
   - [User Conversations List (`GET /chat/title`)](#user-conversations-list-get-chattitle)
   - [Conversation Messages History (`GET /chatHistory/{conversation_id}`)](#conversation-messages-history-get-chathistoryconversation_id)

---

## 1. Global Architecture & Security

- **Base URL**: `http://localhost:8000` (or proxy via Nginx `http://localhost:8080`)
- **Authentication Header**: Bearer JWT token in Authorization header:
  ```http
  Authorization: Bearer <JWT_ACCESS_TOKEN>
  ```
- **Password Security Standard**: Passwords must be at least 10 characters long, containing at least one uppercase letter (`A-Z`), one lowercase letter (`a-z`), one digit (`0-9`), and one special character (`@$!%*?&#`). All passwords are hashed using Argon2id.
- **Financial Precision**: All monetary values use fixed 2-decimal place numeric representations (`Numeric(18, 2)`).
- **Concurrency Control & Idempotency**: Money transfers use database row-level locking (`SELECT ... FOR UPDATE`) and support client-provided `idempotency_key` headers/payloads to prevent double spending and duplicate requests.

---

## 2. Authentication & Account Management

### User Registration (`POST /auth/signup`)
Registers a user with Argon2id password hashing, provisions a wallet account, credits initial **BDT 100,000**, records an initial transaction, produces a double-entry credit ledger record, and creates a welcome notification.

- **Endpoint**: `POST /auth/signup`
- **Headers**: `Content-Type: application/json`
- **Status Code**: `201 Created`

#### Input Schema (`UserCreate`)
| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `full_name` | `string` | Yes | Full display name (2 to 150 chars) | `"Yasin Arafat"` |
| `username` | `string` | Yes | Alphanumeric handle (3 to 50 chars) | `"yasin_arafat_05"` |
| `phone_number` | `string` | Yes | Contact phone number (10 to 20 chars) | `"01700000000"` |
| `email` | `string` (email) | Yes | Valid unique email address | `"yasin@example.com"` |
| `password` | `string` | Yes | Secure password (min 10 chars, uppercase, lowercase, digit, special) | `"SecurePassword123!"` |

##### Request Body Example
```json
{
  "full_name": "Yasin Arafat",
  "username": "yasin_arafat_05",
  "phone_number": "01700000000",
  "email": "yasin@example.com",
  "password": "SecurePassword123!"
}
```

#### Output Schema (`UserResponse`)
```json
{
  "id": "e9b16952-4752-4a7b-a3d8-e7d6ab621111",
  "full_name": "Yasin Arafat",
  "username": "yasin_arafat_05",
  "phone_number": "01700000000",
  "email": "yasin@example.com",
  "account_status": "ACTIVE",
  "created_at": "2026-08-29T10:00:00.000Z"
}
```

---

### User Login (`POST /auth/login`)
Authenticates user using Username, Email, OR Phone number and password.

- **Endpoint**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`
- **Status Code**: `200 OK`

#### Input Schema (`UserLogin`)
```json
{
  "identifier": "yasin_arafat_05",
  "password": "SecurePassword123!"
}
```

#### Output Schema (`TokenResponse`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "e9b16952-4752-4a7b-a3d8-e7d6ab621111",
    "full_name": "Yasin Arafat",
    "username": "yasin_arafat_05",
    "phone_number": "01700000000",
    "email": "yasin@example.com",
    "account_status": "ACTIVE",
    "created_at": "2026-08-29T10:00:00.000Z"
  }
}
```

---

### OAuth2 Form Login (`POST /token`)
OAuth2 spec form-data endpoint for Swagger UI login.

- **Endpoint**: `POST /token`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Form Data**: `username` (identifier) & `password`
- **Output**: `{"access_token": "...", "token_type": "bearer"}`

---

## 3. User Profile & Discovery

### Authenticated User Profile (`GET /users/me`)
Returns current authenticated user profile.

- **Endpoint**: `GET /users/me`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`UserResponse`)**:
  ```json
  {
    "id": "e6a3fbca-98d4-4b43-a609-ec67d87f08d6",
    "full_name": "Yasin Arafat",
    "username": "yasin_arafat_05",
    "phone_number": "01921067682",
    "email": "yasin@gmail.com",
    "account_status": "ACTIVE",
    "created_at": "2026-08-29T05:07:30.733591Z",
    "account": {
      "id": "11111111-2222-3333-4444-555555555555",
      "user_id": "e6a3fbca-98d4-4b43-a609-ec67d87f08d6",
      "account_number": "ACC-9A8B7C6D",
      "balance": 100000.00,
      "available_balance": 100000.00,
      "currency": "BDT",
      "status": "ACTIVE",
      "created_at": "2026-08-29T05:07:30.733591Z"
    }
  }
  ```

---

### User Search (`GET /users/search`)
Search registered users by username, email, or phone substring for send money / request money autocompletion.

- **Endpoint**: `GET /users/search?query=bob&limit=10`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`List[UserSearchResponse]`)**:
  ```json
  [
    {
      "id": "f8a05841-3641-3a6b-92d7-d6c5ab510000",
      "full_name": "Bob Rahman",
      "username": "bob_rahman",
      "phone_number": "01800000000",
      "email": "bob@example.com"
    }
  ]
  ```

---

## 4. Digital Wallet & Money Movement

### Wallet Dashboard (`GET /wallet/dashboard`)
Retrieves account balance, available balance, status, and recent 10 transactions.

- **Endpoint**: `GET /wallet/dashboard`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`WalletDashboardResponse`)**:
  ```json
  {
    "account": {
      "id": "11111111-2222-3333-4444-555555555555",
      "user_id": "e9b16952-4752-4a7b-a3d8-e7d6ab621111",
      "account_number": "ACC-9A8B7C6D",
      "balance": 100000.00,
      "available_balance": 100000.00,
      "currency": "BDT",
      "status": "ACTIVE",
      "created_at": "2026-08-29T10:00:00.000Z"
    },
    "recent_transactions": [
      {
        "id": "77777777-8888-9999-0000-111111111111",
        "reference_id": "TX-20260829-82931",
        "sender_account_id": "11111111-2222-3333-4444-555555555555",
        "receiver_account_id": "22222222-3333-4444-5555-666666666666",
        "amount": 2500.00,
        "currency": "BDT",
        "transaction_type": "TRANSFER",
        "status": "COMPLETED",
        "note": "Lunch payment",
        "created_at": "2026-08-29T10:15:00.000Z"
      }
    ]
  }
  ```

---

### Send Money Transfer (`POST /wallet/transfer`)
Executes atomic money movement between accounts using `SELECT ... FOR UPDATE` row locks, idempotency checks, ledger records, and notifications.

- **Endpoint**: `POST /wallet/transfer`
- **Headers**: `Authorization: Bearer <TOKEN>`, `Content-Type: application/json`

#### Input Schema (`SendMoneyRequest`)
```json
{
  "receiver_identifier": "bob_rahman",
  "amount": 2500.00,
  "note": "Lunch payment",
  "idempotency_key": "KEY-82931-XYZ"
}
```

#### Output Schema (`TransactionResponse`)
```json
{
  "id": "77777777-8888-9999-0000-111111111111",
  "reference_id": "TX-20260829-82931",
  "sender_account_id": "11111111-2222-3333-4444-555555555555",
  "receiver_account_id": "22222222-3333-4444-5555-666666666666",
  "sender_username": "yasin_arafat_05",
  "receiver_username": "bob_rahman",
  "amount": 2500.00,
  "currency": "BDT",
  "transaction_type": "TRANSFER",
  "status": "COMPLETED",
  "idempotency_key": "KEY-82931-XYZ",
  "note": "Lunch payment",
  "created_at": "2026-08-29T10:15:00.000Z"
}
```

---

### Transaction History (`GET /wallet/transactions`)
Returns paginated incoming and outgoing transaction records.

- **Endpoint**: `GET /wallet/transactions?page=1&limit=20`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`List[TransactionResponse]`)**: Array of transaction response objects.

---

### Single Transaction Details (`GET /wallet/transactions/{reference_id}`)
Fetches transaction details by reference string.

- **Endpoint**: `GET /wallet/transactions/TX-20260829-82931`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`TransactionResponse`)**

---

### Double-Entry Ledger Audit Trail (`GET /wallet/ledger`)
Returns double-entry DEBIT and CREDIT audit logs for financial auditing.

- **Endpoint**: `GET /wallet/ledger?page=1&limit=20`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Output Schema (`List[LedgerEntryResponse]`)**:
  ```json
  [
    {
      "id": "abc-123",
      "transaction_id": "77777777-8888-9999-0000-111111111111",
      "account_id": "11111111-2222-3333-4444-555555555555",
      "entry_type": "DEBIT",
      "amount": 2500.00,
      "balance_after": 97500.00,
      "created_at": "2026-08-29T10:15:00.000Z"
    }
  ]
  ```

---

## 5. Money Requests

### Create Money Request (`POST /wallet/request-money`)
Sends a money request to another user with a 24-hour expiration window.

- **Endpoint**: `POST /wallet/request-money`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Input Schema (`MoneyRequestCreate`)**:
  ```json
  {
    "payer_identifier": "bob_rahman",
    "amount": 1200.00,
    "note": "Project reimbursement"
  }
  ```
- **Output Schema (`MoneyRequestResponse`)**:
  ```json
  {
    "id": "33333333-4444-5555-6666-777777777777",
    "requester_id": "e9b16952-4752-4a7b-a3d8-e7d6ab621111",
    "payer_id": "f8a05841-3641-3a6b-92d7-d6c5ab510000",
    "requester_name": "Yasin Arafat",
    "payer_name": "Bob Rahman",
    "amount": 1200.00,
    "note": "Project reimbursement",
    "status": "PENDING",
    "expires_at": "2026-08-30T10:15:00.000Z",
    "created_at": "2026-08-29T10:15:00.000Z"
  }
  ```

---

### Incoming Money Requests (`GET /wallet/requests/incoming`)
Lists incoming money requests targeting the user.

- **Endpoint**: `GET /wallet/requests/incoming`
- **Output Schema (`List[MoneyRequestResponse]`)**

---

### Outgoing Money Requests (`GET /wallet/requests/outgoing`)
Lists outgoing money requests created by the user.

- **Endpoint**: `GET /wallet/requests/outgoing`
- **Output Schema (`List[MoneyRequestResponse]`)**

---

### Accept / Decline Request (`POST /wallet/request-money/{request_id}/action`)
Processes a pending money request. Accepting executes atomic transfer.

- **Endpoint**: `POST /wallet/request-money/33333333-4444-5555-6666-777777777777/action`
- **Input Schema (`MoneyRequestAction`)**:
  ```json
  {
    "action": "ACCEPT",
    "idempotency_key": "REQ_ACCEPT_KEY_99"
  }
  ```
- **Output Schema (`MoneyRequestResponse`)**

---

## 6. In-App Notifications

### Get Notifications (`GET /notifications`)
Lists in-app notifications for the user.

- **Endpoint**: `GET /notifications`
- **Output Schema (`List[NotificationResponse]`)**:
  ```json
  [
    {
      "id": "99999999-0000-1111-2222-333333333333",
      "user_id": "e9b16952-4752-4a7b-a3d8-e7d6ab621111",
      "title": "Account Funded",
      "message": "Welcome to your Digital Wallet! Your account has been credited with BDT 100,000.00 initial balance.",
      "notification_type": "INITIAL_CREDIT",
      "is_read": false,
      "reference_id": "TX-20260829-82931",
      "created_at": "2026-08-29T10:00:00.000Z"
    }
  ]
  ```

---

### Mark Single Notification Read (`PATCH /notifications/{notification_id}/read`)
- **Endpoint**: `PATCH /notifications/99999999-0000-1111-2222-333333333333/read`
- **Output Schema (`NotificationResponse`)**

---

### Mark All Notifications Read (`PATCH /notifications/read-all`)
- **Endpoint**: `PATCH /notifications/read-all`
- **Output**: `{"status": "success", "marked_read_count": 3}`

---

## 7. System Observability & Health

### Health Status Check (`GET /health`)
- **Endpoint**: `GET /health`
- **Output**:
  ```json
  {
    "status": "Healthy",
    "database": "Connected",
    "service": "EduManage API"
  }
  ```

---

## 8. AI Chat & SSE Streaming

### Streaming Chat Response (`POST /chat`)
- **Endpoint**: `POST /chat`
- **Input Schema (`InputMessage`)**:
  ```json
  {
    "message": "Explain atomic database transactions",
    "checkpoint_id": null,
    "workflow_type": "default",
    "resume_data": null
  }
  ```
- **Response Format**: `text/event-stream`

---

### User Conversations List (`GET /chat/title`)
- **Endpoint**: `GET /chat/title`

---

### Conversation Messages History (`GET /chatHistory/{conversation_id}`)
- **Endpoint**: `GET /chatHistory/1`
