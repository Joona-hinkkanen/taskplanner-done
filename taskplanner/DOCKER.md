# TaskPlanner Dockerissa

Tämä hakemisto sisältää TaskPlanner-Django-sovelluksen konttiversion.
Ratkaisu noudattaa Dockerin Django-ohjetta (<https://docs.docker.com/guides/django/>)
sovellettuna tähän projektiin: gunicorn toimii WSGI-palvelimena, whitenoise jakaa
staatiset tiedostot ja tietokantana on PostgreSQL.

## Tiedostot

| Tiedosto | Tarkoitus |
|---|---|
| `Dockerfile` | Rakentaa imagen `python:3.12-slim`-pohjalta, asentaa riippuvuudet ja kopioi koodin. |
| `entrypoint.sh` | Odottaa tietokantaa, ajaa `migrate` + `collectstatic`, luo pääkäyttäjän ja käynnistää gunicornin. |
| `docker-compose.yml` | Kaksi palvelua: `web` (Django) ja `db` (PostgreSQL 16) + pysyvä taltio `pgdata`. |
| `.dockerignore` | Jättää imagen ulkopuolelle mm. `.env`, `__pycache__`, `db.sqlite3`. |
| `.env.docker.example` | Esimerkki ympäristömuuttujista. Kopioi tarvittaessa nimelle `.env`. |

## Vaatimukset

- Docker Desktop (Windows/macOS) tai Docker Engine + Compose (Linux)
- Vähintään ~1 GB vapaata levyä

## Käyttö

Aja komennot tässä hakemistossa (`taskplanner/`):

```bash
# 1. Rakenna image ja käynnistä web + db
docker compose up --build

# 2. Avaa selaimessa
#    http://localhost:8000/
#    http://localhost:8000/admin/
```

Ensimmäinen käynnistys kestää hetken (imagen rakennus + migraatiot).
Kun lokissa näkyy `Listening at: http://0.0.0.0:8000`, sovellus on valmis.

Oletustunnukset (jos `.env`-tiedostoa ei ole):

- käyttäjänimi: `admin`
- salasana: `admin`

> Vaihda tunnukset tiedostossa `.env` ennen kuin käytät ratkaisua muualla kuin omalla koneella.

### Hyödylliset komennot

```bash
docker compose up -d --build     # taustalle
docker compose logs -f web       # seuraa lokeja
docker compose ps                # palvelujen tila
docker compose exec web sh       # komentokuori konttiin
docker compose exec web python manage.py createsuperuser
docker compose down              # pysäytä
docker compose down -v           # pysäytä ja tyhjennä tietokanta
```

## Miten kontti toimii

1. `Dockerfile` asentaa `requirements.txt`:n riippuvuudet omaan kerrokseensa,
   joten uudelleenrakennus on nopea, kun vain koodi muuttuu.
2. `docker-compose.yml` käynnistää Postgresin ja odottaa sen healthcheckiä
   (`pg_isready`) ennen kuin `web` käynnistyy.
3. `entrypoint.sh` odottaa vielä itse tietokantayhteyttä, ajaa migraatiot ja
   `collectstatic`-komennon (whitenoise tarvitsee manifestin, koska `DEBUG=False`).
4. Lopuksi gunicorn käynnistyy: `gunicorn taskplanner.wsgi:application --bind 0.0.0.0:8000`.
5. Sovellus ei aja root-käyttäjänä vaan UID 1000 -käyttäjänä (`app`).

## Testaus (esittelyä varten)

```bash
docker compose up --build
```

1. `http://localhost:8000/` -> ohjautuu kirjautumissivulle.
2. Kirjaudu `admin` / `admin` -> tehtävälista (Kanban) avautuu.
3. `http://localhost:8000/admin/` -> Django-admin, käyttäjä `admin`.
4. Lisää tehtävä ja varmista, että se tallentuu tietokantaan.
5. `docker compose down && docker compose up -d` -> tehtävä on tallessa
   (tietokanta on nimessä `pgdata`).
6. `docker compose ps` -> molemmat palvelut `running`/`healthy`.

## Render + Docker (valinnainen)

Render osaa rakentaa imagen suoraan `Dockerfile`ista:

1. Render Dashboard -> **New** -> **Web Service** -> valitse repo.
2. **Language**: `Docker`.
3. **Root Directory**: `taskplanner`
4. **Dockerfile Path**: `./Dockerfile`
5. **Instance type**: Free.
6. Environment Variables: samat kuin tavallisessa Django-julkaisussa
   (`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=.onrender.com`, `DB_*`,
   `DJANGO_SUPERUSER_*`). Älä aseta `PORT`-muuttujaa: Render välittää sen itse.
7. **Deploy web service**.

Render ajaa kontin `CMD`-komennon ja välittää `PORT`-ympäristömuuttujan.
Jos haluat käyttää sitä, vaihda `CMD` muotoon:

```dockerfile
CMD ["sh", "-c", "gunicorn taskplanner.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
```

## Vianetsintä

| Oire | Syy / ratkaisu |
|---|---|
| `port is already allocated` | Portti 8000 on varattu. Vaihda `docker-compose.yml`:ssä `"8000:8000"` -> `"8080:8000"`. |
| `DisallowedHost` | Lisää osoite `ALLOWED_HOSTS`-muuttujaan (välilyönnillä erotettuna). |
| `relation ... does not exist` | Migraatiot eivät ajautuneet. `docker compose logs web` ja aja `docker compose exec web python manage.py migrate`. |
| Admin-sivu ilman tyylejä | `collectstatic` puuttuu tai `DEBUG=False` ilman manifestia. Aja `docker compose exec web python manage.py collectstatic --noinput`. |
| Tietokanta ei käynnisty | `docker compose logs db`; vanha taltio voi estää. `docker compose down -v` ja uudelleen. |
