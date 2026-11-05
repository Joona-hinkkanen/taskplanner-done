#!/bin/sh
# Kontin käynnistyskripti: odottaa tietokantaa, ajaa migraatiot,
# kerää staatiset tiedostot ja käynnistää gunicornin.
set -eu

if [ "${DB_ENGINE:-}" = "django.db.backends.postgresql" ]; then
    echo "Odotetaan tietokantaa (${DB_HOST:-db}:${DB_PORT:-5432})..."
    python - <<'PY'
import os
import sys
import time

import psycopg2

for attempt in range(1, 31):
    try:
        psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ.get("DB_HOST", "db"),
            port=os.environ.get("DB_PORT", "5432"),
        ).close()
        print(f"Tietokanta vastaa (yritys {attempt}).")
        break
    except psycopg2.OperationalError as exc:
        print(f"  ei vielä yhteyttä (yritys {attempt}/30): {exc}".strip(), flush=True)
        time.sleep(2)
else:
    sys.exit("VIRHE: tietokantaan ei saatu yhteyttä 60 sekunnissa.")
PY
fi

echo "Ajetaan migraatiot..."
python manage.py migrate --noinput

echo "Kerätään staatiset tiedostot..."
python manage.py collectstatic --noinput

# Superuser luodaan vain, jos tunnukset on annettu ympäristömuuttujina.
# Jos käyttäjä on jo olemassa, komento epäonnistuu -> ohitetaan.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "Varmistetaan pääkäyttäjä (${DJANGO_SUPERUSER_USERNAME})..."
    python manage.py createsuperuser --noinput || echo "  pääkäyttäjä on jo olemassa, ohitetaan."
fi

echo "Käynnistetään sovellus: $*"
exec "$@"
