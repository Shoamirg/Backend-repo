# Mobile customer API (React Native / Expo)

Base URL: `https://BACKEND-DOMAIN/api/v1/customer`. Bodies are JSON unless
noted. Errors look like `{"error": {"code": "...", "detail": "..."}}`.

Every customer session belongs to an email + password account. Telegram sign-in
has been removed.

## Sign-up

A garage already has the customer on file (name, phone, email). The app proves
the user is that person with an SMS code.

1. `POST /auth/signup/start` `{email, phone}` → **202** `{detail, expires_in}`.
   Always 202, whether or not anything matched (no account probing). The SMS
   is sent after the response.
2. `POST /auth/signup/complete` `{email, phone, code, password}` → **201** token pair
   (`access_token`, `refresh_token`, `customer`).
   - `409 GARAGE_SELECTION_REQUIRED`: the details exist at several garages.
     `error.garages` is `[{service_center_id, name}]`; resend with
     `service_center_id` and the same code.
   - `400 INVALID_VERIFICATION_CODE`: wrong, expired, used, or 5 wrong tries.
   - `404 SIGNUP_PROFILE_NOT_FOUND`, `409 ACCOUNT_ALREADY_EXISTS`.

Phone may be typed with or without `+998`. Password: 10–72 bytes. Code: 6 digits,
valid 10 minutes; a new `start` replaces the previous code. At most 3 codes per
phone and per email every 15 minutes (then `429` with `Retry-After`).

## Sign-in and sessions

- `POST /auth/login` `{email, password}` **or** `{phone, password}` → token pair.
- `POST /auth/refresh` `{refresh_token}` → new pair. **Always store the new
  refresh token**: the old one stops working, and replaying it signs the
  session out.
- `POST /auth/logout` with `Authorization: Bearer <refresh or access token>`.

Access tokens live 30 minutes. A session stays alive while the app refreshes at
least every 60 days, up to 365 days total, then the user signs in again.
Keep tokens in `expo-secure-store` / Keychain, not AsyncStorage.

## Password

- Forgot: `POST /auth/password/reset/start` `{email}` or `{phone}` → 202 (SMS to
  the phone on the record), then `POST /auth/password/reset/complete`
  `{email | phone, code, new_password}` → 200. Every device is signed out.
  A phone shared by logins at two garages must reset by email.
- Change (signed in): `POST /me/password` `{current_password, new_password}` →
  new token pair for this device; other devices are signed out.

## Push notifications (Expo)

- After sign-in: `POST /devices` `{token: "ExponentPushToken[...]", platform: "ios" | "android"}`.
  Registering the same token from another account moves it to that account.
- On sign-out: `DELETE /devices` `{token}`.
- Pushes carry `data: {type, id}` to deep-link: `appointment`, `estimate`,
  `invoice`, `conversation`, `case`. Sent for: appointment confirmed, completed
  ("Your car is ready") or cancelled; estimate sent; invoice issued; a garage
  reply in a conversation; roadside case status changes.

## Photos

- `POST /files` as `multipart/form-data` with field `file` → **201**
  `{id, content_type, size_bytes, url}`. JPEG, PNG, WebP or HEIC, up to 10 MB
  (`422 UNSUPPORTED_FILE_TYPE`, `413 FILE_TOO_LARGE`).
- Attach to a message: `POST /messages/{conversation_id}`
  `{body?, attachments: [{file_id, label?}]}` (up to 5 photos; text optional).
- Download with the same bearer token: `GET /files/{id}`. Works for photos the
  customer uploaded and photos the garage sent them.

## Delete account (App Store / Play requirement)

`DELETE /me` with body `{password}` → 200. The login, sessions and push devices
are removed and the profile is anonymized; the garage keeps invoices and
service history. Sign the user out locally after this call.

## Other codes

- `401`: token invalid or signed out → refresh once, then send to login.
- `429 RATE_LIMITED` with `Retry-After` header.
- `503 SMS_UNAVAILABLE`: SMS not configured.
