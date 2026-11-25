# primstav

En liten Mastodon-bot som poster dagens merkedag fra primstaven hver morgen kl. 08 (norsk tid).

Merkedagene ligger hardkodet i `merkedager.json`, hentet fra tabellen på
[no.wikipedia.org/wiki/Primstav](https://no.wikipedia.org/wiki/Primstav). Fotnoter er fjernet, og noen
få rader er ryddet for hånd. Wikipedia-lenker som er røde lenker på siden er utelatt.

Boten bruker bare Python-standardbiblioteket (3.9+), så det er ingenting å installere.

```sh
python3 primstav.py --dry-run                 # vis dagens post
python3 primstav.py --dry-run --dato 2026-07-29
```

## Autentisering

Boten bruker et vanlig OAuth-access-token for bot-kontoen, sendt som `Authorization: Bearer …`.
Tokenet utløper ikke, og kan trekkes tilbake når som helst.

Slik lager du det:

1. Logg inn som bot-kontoen på snabel.party.
2. Gå til **Innstillinger → Utvikling → Ny applikasjon**.
3. Gi den et navn (f.eks. `primstav`), og fjern alle scopes unntatt **`write:statuses`**.
4. Lagre, åpne applikasjonen og kopier **Tilgangsnøkkelen din** (access token).
5. Legg den i `/home/mastodon/primstav/.env` (se `.env.example`) på serveren.

`.env` skal bare kunne leses av `mastodon`-brukeren (`chmod 600`).

Husk også å huke av for «Dette er en bot-konto» under profilinnstillingene.

## Drift på snabel.party

Koden ligger i `/home/mastodon/primstav` og kjøres som `mastodon`-brukeren av en systemd-timer.

Første gangs oppsett (som root):

```sh
sudo -u mastodon git clone https://github.com/arnemart/primstav.git /home/mastodon/primstav
sudo -u mastodon cp /home/mastodon/primstav/.env.example /home/mastodon/primstav/.env
chmod 600 /home/mastodon/primstav/.env   # og fyll inn MASTODON_TOKEN
ln -s /home/mastodon/primstav/deploy/primstav.service /home/mastodon/primstav/deploy/primstav.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now primstav.timer
```

Oppdatering:

```sh
sudo -u mastodon git -C /home/mastodon/primstav pull
systemctl daemon-reload
```

Nyttige kommandoer:

```sh
systemctl list-timers primstav.timer      # neste kjøring
systemctl start primstav.service          # post nå
journalctl -u primstav.service            # logg
```

Jobben setter en `Idempotency-Key` basert på datoen, så den poster ikke dobbelt om den kjøres
flere ganger rett etter hverandre.
