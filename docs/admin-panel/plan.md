# Plan: staff authentication and the admin panel

Do the phases in order. Each phase ends with something you can run. Check a box when the
"done when" line is true. Decisions and reasons are in [`README.md`](README.md).

## Phase 0. Decisions

- [ ] Read `README.md` and answer the open questions at the end.
- [ ] Add `JWT_SECRET` (and a cookie lifetime setting) to `Settings`, `.env.example` and
      `compose.yaml`. Tests set their own value.

## Phase 1. Backend: staff authentication

- [ ] **Domain:** add `NewStaffUser` and its rules (email normalised to lowercase, name,
      password length 12 to 128). `StaffUser` and `StaffRole` already exist.
- [ ] **Ports:** `StaffRepository` (`get_by_email`, `get_by_id`, `add`, `touch_last_login`),
      `PasswordHasher` (`hash`, `verify`), and `TokenService` (`issue`, `read`) as Protocols.
- [ ] **Infrastructure:** `SqlStaffRepository`, `Argon2PasswordHasher`, `JwtTokenService`.
- [ ] **Use cases:** `AuthenticateStaff`, `GetCurrentStaff`, `CreateStaff`. Login hashes a
      dummy password when the email is unknown.
- [ ] **API:** `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`; dependencies
      `get_current_staff` and `require_admin`; cookie settings in one place.
- [ ] **Command:** `create-admin` next to the seed script. It reads the password from a
      prompt, not from an argument.
- [ ] **Tests:** unit, repository and API tests from the testing strategy.

Done when: `pytest`, `ruff` and `mypy` pass, and with `curl` you can log in, call
`/auth/me` with the cookie, and get 401 without it.

## Phase 2. Backend: lead management

- [ ] `LeadRepository`: `list(status, limit, offset)`, `count(status)`, `get(id)`,
      `update_status(id, status)`.
- [ ] Domain: allowed status transitions (a method on `Lead`).
- [ ] Use cases: `ListLeads`, `GetLead`, `ChangeLeadStatus`.
- [ ] Endpoints `GET /leads`, `GET /leads/{id}`, `PATCH /leads/{id}`, all behind login.
      `POST /leads` stays public.
- [ ] `POST /staff` (admin only) with a test that a baker gets 403.
- [ ] Tests for 401, 403, 404, 409, 422, pagination and the status filter.

Done when: the `api-types` CI job passes after you regenerate `frontend/src/lib/api/schema.d.ts`.

## Phase 3. The Vite admin app (`admin/`)

- [ ] `pnpm create vite admin` (React + TypeScript). Add Tailwind and shadcn, as in the shop.
- [ ] Dev proxy: `/api` goes to `http://localhost:8000`, prefix removed.
- [ ] Types: `openapi-typescript` and `openapi-fetch`; the client sends cookies. Add a
      `gen:api` script like the shop's.
- [ ] Router with the pages `/login`, `/` (leads list), `/leads/:id`.
- [ ] Session: call `GET /auth/me` on start; a route guard redirects to `/login` on 401;
      one place handles 401 for every request.
- [ ] TanStack Query: the leads list (with pagination and status filter), the detail page,
      and a mutation for the status that refreshes the list.
- [ ] Login form and status form with validation, and server errors under the fields.
- [ ] Loading, empty and error states on every screen. Logout button.

Done when: you log in as the admin, see leads made through the shop form, change a status,
and log out.

## Phase 4. Tests for the admin app

- [ ] Vitest for pure functions and small components.
- [ ] Playwright (`admin/e2e/`): wrong password, correct login, open a lead, change status,
      logout, redirect when logged out.
- [ ] The e2e job creates an admin with `create-admin` before the tests run.

## Phase 5. Deployment and CI

- [ ] Dockerfile that builds `admin/` into static files; a Caddy route for it, with `/api`
      proxied to the backend.
- [ ] CI job for `admin/`: typecheck, lint, build, Vitest.
- [ ] Extend the `api-types` job to check `admin/src/api/schema.d.ts` too.
- [ ] Rate limit on `POST /auth/login`.
- [ ] Final pass over the security checklist in `README.md`.
