# sbtb — clients

JS monorepo for all client apps (web, future mobile) and shared packages.

## Layout

- `apps/web/` — Next.js 15 web app
- `packages/` — shared TypeScript packages (empty for now)

## Setup

```bash
cd clients
pnpm install
```

## Development

```bash
pnpm dev                      # all apps
pnpm --filter @sbtb/web dev   # just the web app
```

## Lint / format / typecheck

```bash
pnpm lint
pnpm format
pnpm typecheck
```
