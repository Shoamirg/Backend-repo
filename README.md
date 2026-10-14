# GarageOS backend

GarageOS API: Python/FastAPI, PostgreSQL, Redis, JWT sessions and role/garage access controls.

Railway uchun repository rooti `/`, Dockerfile shu yerda. Deploydan oldin
PostgreSQL/Redis reference URL, private SECRET_KEY va frontend HTTPS CORS originini
sozlang. Pre-deploy command: `alembic upgrade head`; healthcheck: `/ready`.

To'liq maydonlar va tartib: [Railway yo'riqnomasi](RAILWAY.md).
Haqiqiy servis/xodimlarni yaratish: [operator ko'rsatmasi](OPERATIONS.md).

API: `/api/v1`; Swagger: `/docs`; liveness: `/health`; readiness: `/ready`.
Productionda demo va debug o'chirilgan. Migratsiya avtomatik foydalanuvchi yaratmaydi.

## Tekshiruv

Testlar va yordamchi QA fixture'lari saqlangan. Lokal testlar uchun alohida
PostgreSQL `garage_test` bazasi, Redis va `ENVIRONMENT=test` kerak.
`requirements-dev.txt`ni o'rnatib, migratsiya qiling. Faqat o'sha test bazasida
`python -m app.seeds.demo --fresh`, keyin `python -m pytest -q` bajariladi.
Linux Docker rehearsal: `python scripts/test_railway_backend.py`.

Yangi Railway projectdagi deploy, HTTPS edge, real akkaunt va backup qabuli
alohida bajariladi. Hozirgi push shu backendni joylash uchun tayyorlaydi.
