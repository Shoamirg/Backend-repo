# Mobile customer auth (React Native)

Base URL: `https://BACKEND-DOMAIN/api/v1/customer`. All bodies are JSON.
Errors look like `{"error": {"code": "...", "detail": "..."}}`.

## Sign-up

A garage already has the customer on file (name, phone, email). The app proves
the user is that person with an SMS code.

1. `POST /auth/signup/start` `{email, phone}` → **202** `{detail, expires_in}`.
   Always 202, whether or not anything matched (no account probing).
2. `POST /auth/signup/complete` `{email, phone, code, password}` → **201** token pair
   (`access_token`, `refresh_token`, `customer`).
   - `409 GARAGE_SELECTION_REQUIRED`: the details exist at several garages.
     `error.garages` is `[{service_center_id, name}]`; resend with
     `service_center_id` and the same code.
   - `400 INVALID_VERIFICATION_CODE`: wrong, expired, used, or 5 wrong tries.
   - `404 SIGNUP_PROFILE_NOT_FOUND`, `409 ACCOUNT_ALREADY_EXISTS`.

Phone may be typed with or without `+998`. Password: 10–72 bytes. Code: 6 digits,
valid 10 minutes; a new `start` replaces the previous code.

## Sign-in and sessions

- `POST /auth/login` `{email, password}` → token pair.
- `POST /auth/refresh` `{refresh_token}` → new pair. **Always store the new
  refresh token**: the old one stops working, and replaying it signs the
  session out.
- `POST /auth/logout` with `Authorization: Bearer <refresh or access token>`.

Access tokens live 30 minutes. A session stays alive while the app refreshes at
least every 60 days, up to 365 days total, then the user signs in again.
Keep tokens in `expo-secure-store` / Keychain, not AsyncStorage.

## Password

- Forgot: `POST /auth/password/reset/start` `{email}` → 202 (SMS to the phone on
  the record), then `POST /auth/password/reset/complete`
  `{email, code, new_password}` → 200. Every device is signed out.
- Change (signed in): `POST /me/password` `{current_password, new_password}` →
  new token pair for this device; other devices are signed out.

## Delete account (App Store / Play requirement)

`DELETE /me` with body `{password}` → 200. The login and all sessions are
removed and the profile is anonymized; the garage keeps invoices and service
history. Sign the user out locally after this call.

## Other codes

- `401`: token invalid or signed out → refresh once, then send to login.
- `429 RATE_LIMITED` with `Retry-After` header.
- `503 SMS_UNAVAILABLE`: SMS not configured or Eskiz down.
