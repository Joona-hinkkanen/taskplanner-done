# TaskPlanner - Django-sovellus kontissa
# Perustuu Dockerin omaan Django-ohjeeseen: https://docs.docker.com/guides/django/
FROM python:3.12-slim

# Tulosteet suoraan lokiin (ei puskurointia) eikä .pyc-tiedostoja levylle
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Riippuvuudet omaan kerrokseensa -> docker build käyttää välimuistia,
# kun vain sovelluskoodi muuttuu.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sovelluskoodi
COPY . .

# Korjataan mahdolliset Windows-rivinvaihdot ja annetaan suoritusoikeus,
# luodaan lisäksi tavallinen käyttäjä (ei ajeta rootina).
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && useradd --create-home --uid 1000 app \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# Paikallisesti kuunnellaan porttia 8000, pilvessä (Render) Renderin antamaa $PORT-muuttujaa.
CMD ["sh", "-c", "exec gunicorn taskplanner.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --access-logfile -"]
