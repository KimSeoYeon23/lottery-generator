# lottery-generator

A Korean lottery companion app for generating Lotto 6/45 and Pension Lottery 720+ number sets, reviewing draw statistics, and optionally preparing selected tickets for purchase through a local Django service.

This project is maintained as an open source tool for learning, automation, and personal productivity around lottery number generation workflows. It does not predict winning numbers, improve lottery odds, or guarantee any prize.

## Features

- Generate Lotto 6/45 number sets with multiple statistical strategies.
- Generate Pension Lottery 720+ group and digit combinations.
- Display historical frequency, hot/cold numbers, and sum-range statistics.
- Save selected Lotto tickets locally before purchase.
- Check balance and submit purchase requests through the Dhlottery web flow.
- Run as a Dockerized Django app with a React/Vite frontend.

## Responsible Use

Lottery drawings are games of chance. The generated numbers are statistical references only and should be used for entertainment or experimentation.

Before using this project, read [RESPONSIBLE_USE.md](RESPONSIBLE_USE.md).

Key points:

- Do not treat generated numbers as predictions.
- Do not spend money you cannot afford to lose.
- Review every ticket manually before purchase.
- Keep account credentials private and use this app only on a trusted machine.
- Follow the terms and rules of the lottery service you access.

## Security Notes

The app can store lottery account credentials locally at `~/.lottery/credentials.json` when the credential save API is used. The file is created with owner-only permissions, but local credential storage is still sensitive.

Security-sensitive areas include:

- Account credential handling.
- Session cookies and login automation.
- Balance lookup and purchase request flows.
- External service changes that may affect request behavior.

Please read [SECURITY.md](SECURITY.md) before reporting vulnerabilities or using the purchase-related features.

## Project Structure

```text
.
+-- backend/              # Django app, generation logic, stats, purchase client
+-- frontend/             # React/Vite frontend
+-- Dockerfile            # Production-style multi-stage build
+-- Dockerfile.dev        # Development backend image
+-- docker-compose.yml    # Single app service
+-- docker-compose.dev.yml
```

## Local Development

### Docker

```sh
docker compose up --build
```

The app is served at:

```text
http://localhost:8000
```

### Development Compose

```sh
docker compose -f docker-compose.dev.yml up --build
```

Backend:

```text
http://localhost:8000
```

Frontend:

```text
http://localhost:5173
```

## Frontend

```sh
cd frontend
pnpm install
pnpm run dev
```

See [frontend/README.md](frontend/README.md) for frontend-specific notes.

## Backend

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

## API Overview

- `POST /api/generate` - generate Lotto and Pension Lottery numbers.
- `GET /api/stats` - return statistics used by the UI.
- `POST /api/save-credentials` - save local account credentials.
- `POST /api/balance` - check account balance.
- `POST /api/buy` - submit selected Lotto tickets.
- `POST /api/buy-pension` - submit Pension Lottery group selections.

## Open Source Maintenance Goals

This repository is intended to remain public and maintainable. Near-term maintenance priorities include:

- Improving documentation for setup, limitations, and safe use.
- Adding tests around number generation and API behavior.
- Reviewing credential storage and purchase flows for security risks.
- Keeping dependencies and deployment files up to date.
- Making release notes and issue triage easier for contributors.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
