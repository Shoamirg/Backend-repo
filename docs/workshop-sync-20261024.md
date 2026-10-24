# Workshop API synchronization

This update brings the workshop, staff service assignments, tenant-scoped
reference data and Telegram gateway from GarageOS main commit `c02d410` into
the standalone Railway backend. Existing mobile SMS verification, phone
sign-in, uploaded files, push devices and sliding customer sessions are kept.

Migration `f6a7b8c9d0e1` follows `d1e2f3a4b5c6`, so `alembic upgrade head`
applies the mobile migrations before adding `users.service_types`. Use the
existing Railway pre-deploy migration command. No seed/reset command is part
of deployment.

The Telegram gateway remains disabled unless `TELEGRAM_WEBHOOK_SECRET` is
configured privately; Telegram media also requires the existing bot token.
Keep SMS/push providers and signing secrets in Railway variables.

After deployment, verify `/ready`, `/version`, authenticated staff and
mechanic workflows, and that `/openapi.json` includes `/api/v1/workshop/jobs`
and `/api/v1/staff/mechanics`. A successful Git push is not proof that the
Railway deployment has completed.
