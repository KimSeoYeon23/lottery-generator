# lottery-generator frontend

React/Vite frontend for `lottery-generator`.

The UI lets users generate Lotto 6/45 and Pension Lottery 720+ number sets, review draw statistics, select Lotto tickets, and use the local backend for balance and purchase-related workflows.

## Responsible Use

Generated numbers are not predictions and do not improve the odds of winning. The frontend should keep that message visible in user-facing flows, especially around generation and purchase actions.

See the root [RESPONSIBLE_USE.md](../RESPONSIBLE_USE.md) and [SECURITY.md](../SECURITY.md).

## Development

```sh
pnpm install
pnpm run dev
```

The development server runs at:

```text
http://localhost:5173
```

The Vite dev server proxies `/api` requests to the Django backend configured in `vite.config.js`.

## Scripts

- `pnpm run dev` - start the Vite dev server.
- `pnpm run build` - build the frontend into `dist/`.
- `pnpm run lint` - run ESLint.
- `pnpm run preview` - preview the production build.
