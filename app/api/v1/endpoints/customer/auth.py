"""Customer sign-in for the Telegram Mini App.

``/telegram`` verifies the launch initData and returns a token pair when the
Telegram user is already linked; otherwise it 404s with ``TELEGRAM_NOT_LINKED``
so the client shows the phone-linking screen, which posts to ``/link``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.customer_deps import get_customer_auth_service
from app.api.logout_proof import logout_proof
from app.schemas.auth import LogoutRequest, LogoutResponse
from app.core.config import settings
from app.core.rate_limit import auth_rate_limit
from app.exceptions import NotFoundError
from app.schemas.customer_portal import (
    DevSignInRequest,
    LinkRequest,
    RefreshRequest,
    TelegramSignInRequest,
    TokenResponse,
)
from app.services.customer_auth_service import CustomerAuthService

router = APIRouter()


@router.post("/logout", response_model=LogoutResponse, summary="Revoke this customer session")
async def logout(request: Request, body: LogoutRequest | None = None,
                 auth: CustomerAuthService = Depends(get_customer_auth_service)) -> LogoutResponse:
    await auth.logout(logout_proof(request, body))
    return LogoutResponse()


@router.post(
    "/telegram",
    response_model=TokenResponse,
    summary="Sign in with Telegram initData",
    dependencies=[Depends(auth_rate_limit)],
)
async def sign_in_telegram(
    body: TelegramSignInRequest,
    auth: CustomerAuthService = Depends(get_customer_auth_service),
) -> TokenResponse:
    return TokenResponse(**await auth.authenticate_telegram(body.init_data))


@router.post(
    "/link",
    response_model=TokenResponse,
    summary="Link Telegram to a customer by phone",
    dependencies=[Depends(auth_rate_limit)],
)
async def link_account(
    body: LinkRequest,
    auth: CustomerAuthService = Depends(get_customer_auth_service),
) -> TokenResponse:
    if not settings.TELEGRAM_PHONE_LINKING_ENABLED:
        raise NotFoundError("Not found")
    return TokenResponse(**await auth.link_by_phone(body.init_data, body.phone))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh a customer token pair",
    dependencies=[Depends(auth_rate_limit)],
)
async def refresh(
    body: RefreshRequest,
    auth: CustomerAuthService = Depends(get_customer_auth_service),
) -> TokenResponse:
    return TokenResponse(**await auth.refresh(body.refresh_token))


@router.post("/dev", response_model=TokenResponse, summary="DEBUG-only sign-in (no Telegram)")
async def dev_sign_in(
    body: DevSignInRequest | None = None,
    auth: CustomerAuthService = Depends(get_customer_auth_service),
) -> TokenResponse:
    # Never expose this outside development — 404 so it's indistinguishable
    # from a route that doesn't exist.
    if settings.ENVIRONMENT != "development" or not settings.DEBUG or not settings.DEV_AUTH_ENABLED:
        raise NotFoundError("Not found")
    return TokenResponse(**await auth.dev_authenticate(body.telegram_id if body else None))

from app.schemas.customer_account import CustomerPasswordLogin

@router.post('/login', response_model=TokenResponse, dependencies=[Depends(auth_rate_limit)])
async def password_login(body: CustomerPasswordLogin, auth: CustomerAuthService = Depends(get_customer_auth_service)):
    return await auth.authenticate_password(str(body.email), body.password)


# ── mobile self-service: sign-up and password reset over SMS codes ─────────
from app.core.config import settings as _settings
from app.core.rate_limit import rate_limit
from app.schemas.customer_account import (
    CodeSent, PasswordResetComplete, PasswordResetStart, SignupComplete, SignupStart,
)
from app.services.customer_account_lifecycle import CustomerAccountLifecycle

# Per-IP ceiling sized for carrier NAT; per-phone/email limits live in the service.
account_rate_limit = rate_limit(limit=30, window=60, scope="customer-account")


def _code_sent() -> CodeSent:
    return CodeSent(expires_in=_settings.VERIFICATION_CODE_TTL_SECONDS)


@router.post('/signup/start', status_code=202, response_model=CodeSent,
             dependencies=[Depends(account_rate_limit)],
             summary="Send an SMS code to the phone on the matching garage record")
async def signup_start(body: SignupStart, auth: CustomerAuthService = Depends(get_customer_auth_service)):
    await CustomerAccountLifecycle(auth.uow).start_signup(str(body.email), body.phone)
    return _code_sent()


@router.post('/signup/complete', status_code=201, response_model=TokenResponse,
             dependencies=[Depends(account_rate_limit)],
             summary="Confirm the SMS code, set a password and sign in")
async def signup_complete(body: SignupComplete, auth: CustomerAuthService = Depends(get_customer_auth_service)):
    return await CustomerAccountLifecycle(auth.uow).complete_signup(
        str(body.email), body.phone, body.code, body.password, body.service_center_id)


@router.post('/password/reset/start', status_code=202, response_model=CodeSent,
             dependencies=[Depends(account_rate_limit)],
             summary="Send a reset code to the phone on the account")
async def password_reset_start(body: PasswordResetStart, auth: CustomerAuthService = Depends(get_customer_auth_service)):
    await CustomerAccountLifecycle(auth.uow).start_reset(str(body.email))
    return _code_sent()


@router.post('/password/reset/complete', response_model=LogoutResponse,
             dependencies=[Depends(account_rate_limit)],
             summary="Set a new password with the SMS code; signs out every device")
async def password_reset_complete(body: PasswordResetComplete, auth: CustomerAuthService = Depends(get_customer_auth_service)):
    await CustomerAccountLifecycle(auth.uow).complete_reset(str(body.email), body.code, body.new_password)
    return LogoutResponse()
