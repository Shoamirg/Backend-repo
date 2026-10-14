# Railway operatori

Migratsiyadan keyin haqiqiy servis/xodim uchun `provisioning.example.json`ga qarab
private manifest tayyorlang. Backend konteyneridagi `/app` ichida bajaring:

```bash
python -m app.commands.provision --config /PRIVATE/garage.local.json
python -m app.commands.provision --config /PRIVATE/garage.local.json --apply
```

Manifestda password qiymati yozilmaydi: undagi `password_env` nomlari uchun
Railway private Variables ishlatiladi. Staff paroli 12–72 UTF-8 byte chegarasida,
kamida 12 belgi bo'ladi. Dry-run natijasini ko'rib, so'ng apply qiling.
Oddiy staff avtomatik superadmin bo'lmaydi. Platform operatori uchun alohida
`python -m app.commands.enroll_platform --help` CLI mavjud.

SECRET_KEY redeploylarda saqlanadi. Real ma'lumotdan oldin database backupi va
alohida restore tekshiruvi, monitoring va javobgar operator belgilanadi.
Railway deploy healthcheck'i doimiy monitoring emas.

Old image'ga qaytishdan oldin joriy schema bilan mosligini tekshiring.
Oddiy rollbackda database reset, destructive downgrade yoki demo seed bajarmang.
`tests/support/source-operations` ichidagilar regressiya fixture'lari;
ular Railway projectga production backup xizmatini o'rnatmaydi.
