# Mozilla Observatory: Migration Plan to Grade A

**Goal:** Take https://joemattiello.dev from Observatory grade C / score ~50 to grade A (90+).

**Why this is needed:** GitHub Pages does not let you set custom HTTP response headers. Observatory grades you on headers like `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Permissions-Policy`, and `Referrer-Policy`. The first four of those **must be sent as real HTTP headers** — browsers explicitly ignore them when set via `<meta http-equiv>`. So the only paths to A are:

1. Put something in front of GitHub Pages that can add headers (Cloudflare proxy), or
2. Move off GitHub Pages to a host that supports a `_headers` file (Cloudflare Pages, Netlify, etc.), or
3. Stay on GitHub Pages and accept a B.

The three options below are ranked best to worst for this site.

---

## Option A — Cloudflare proxy in front of GitHub Pages (RECOMMENDED)

Keep your existing GitHub Actions deploy pipeline exactly as-is. Cloudflare sits in front, adds the security headers on every response, and nothing about your build / repo / workflow changes.

**Effort:** ~30 minutes, all in the Cloudflare dashboard. No code changes.

**Result:** Observatory A (90+).

### Pros
- Zero changes to your deploy pipeline. `pages.yml` keeps working untouched.
- Free tier covers everything you need.
- Bonus: caching, DDoS protection, free analytics, image polishing — all optional.
- You can roll back in 5 minutes by flipping the Cloudflare proxy off (orange cloud → grey cloud).

### Cons
- DNS now lives at Cloudflare (you have to update nameservers at your domain registrar).
- One more vendor in the request path (but Cloudflare is essentially zero-downtime infra).
- CSP needs `'unsafe-inline'` for now (see CSP Risks section) — same caveat as Option B.

### What you do, step by step

1. **Create a Cloudflare account** at https://dash.cloudflare.com/sign-up (free plan is fine).

2. **Add your site as a zone.**
   - Cloudflare Dashboard → top-right `+ Add` → `Add a domain`.
   - Enter `joemattiello.dev`, click `Continue`.
   - Pick the **Free** plan, click `Continue`.
   - Cloudflare will scan and import your existing DNS records. Verify `joemattiello.dev` (and `www`) point to GitHub Pages (`185.199.108.153`, `.109`, `.110`, `.111`, or CNAME `joemattiello.github.io`). Click `Continue`.

3. **Switch nameservers at your domain registrar** (wherever you bought joemattiello.dev — Namecheap, GoDaddy, Cloudflare Registrar, etc.).
   - Cloudflare gives you two nameservers (something like `xxx.ns.cloudflare.com` and `yyy.ns.cloudflare.com`).
   - Log into your registrar, find DNS / nameserver settings for `joemattiello.dev`, replace the existing nameservers with Cloudflare's two.
   - Save. DNS propagation typically completes in 5–60 minutes; Cloudflare will email you when active.

4. **Verify proxy is on.**
   - Once active, Cloudflare Dashboard → `joemattiello.dev` → `DNS` → `Records`.
   - Both the apex `joemattiello.dev` record and `www` should have an **orange cloud** icon (proxied). If grey, click it to turn orange.

5. **Force HTTPS.** Dashboard → `SSL/TLS` → `Overview` → set encryption mode to **Full** (not Flexible — Flexible can break GitHub Pages). Then `SSL/TLS` → `Edge Certificates` → enable **Always Use HTTPS** and **Automatic HTTPS Rewrites**.

6. **Add the security headers via Transform Rules.**
   - Dashboard → `Rules` → `Transform Rules` → `Modify Response Header` tab → `Create rule`.
   - Rule name: `Security headers for joemattiello.dev`.
   - When incoming requests match: `Custom filter expression` → enter `(http.host eq "joemattiello.dev") or (http.host eq "www.joemattiello.dev")`.
   - Then... → click `+ Add` and add each of the headers from `cloudflare-transform-rules.json` in this repo. For each entry under `set_headers`, choose action **`Set static`**, paste the header name, paste the value. Repeat 8 times (one per header).
   - Click `Deploy`.

7. **Validate.** From a terminal: `curl -I https://joemattiello.dev/`. You should see all 8 headers. Then re-run https://observatory.mozilla.org/analyze/joemattiello.dev — should be A or A+.

**What gets fixed:** every Observatory finding except subresource integrity (SRI), which is an A+ bonus and not required for an A.

---

## Option B — Full migration to Cloudflare Pages

Replace GitHub Pages entirely. Cloudflare Pages reads a `_headers` file (already created in this repo at `static-site/_headers`) and applies it to every response. Same end result as Option A but you've also moved hosting.

**Effort:** ~1–2 hours. New deploy workflow, DNS change, validate.

**Result:** Observatory A (90+).

### Pros
- Headers live in the repo (`_headers` file is checked in) — visible alongside the code, reviewable in PRs.
- Free tier (500 builds/month, unlimited bandwidth).
- Same Cloudflare benefits as Option A (caching, DDoS, etc.).

### Cons
- More moving pieces than Option A. New deploy workflow to maintain, new build settings to configure.
- You give up the GitHub-Pages-specific niceties (custom 404, gh-pages branch as a deploy log).
- If Cloudflare Pages has a build outage, you've coupled your deploy to it.

### What you do, step by step

1. **Set up Cloudflare account + zone + nameservers** — exactly steps 1–3 of Option A above.

2. **Create the Pages project.**
   - Dashboard → `Workers & Pages` → `Create` → `Pages` tab → `Connect to Git`.
   - Authorize Cloudflare on your GitHub account, pick `JoeMatt/joematt.github.io`.
   - Project name: `joematt-dev` (or anything).
   - Production branch: `master`.
   - Build settings:
     - Framework preset: `None`.
     - Build command: *(leave empty — site is pre-built static under `static-site/`)*.
     - Build output directory: `static-site`.
   - Click `Save and Deploy`. First deploy takes ~1 minute.

3. **Bind your custom domain.**
   - Cloudflare Pages project → `Custom domains` → `Set up a custom domain` → enter `joemattiello.dev`. Confirm.
   - Repeat for `www.joemattiello.dev`. Cloudflare will create the DNS records automatically.

4. **Verify `_headers` is being applied.**
   - The file `static-site/_headers` is already in this repo and ships with each deploy.
   - `curl -I https://<project>.pages.dev/` (the preview URL) — should show all security headers. Once custom domain is live, same check on `https://joemattiello.dev/`.

5. **Disable the GitHub Pages deploy.**
   - In `.github/workflows/pages.yml`, either delete the workflow file or comment out the `on:` trigger so it stops running.
   - Don't do this until step 4 is green.

6. **Re-run Observatory.** Should be A.

### Proposed workflow file

A separate file `.github/workflows/cloudflare-pages.yml.proposed` is **not** included in this repo — Cloudflare Pages has a built-in Git integration that handles deploys automatically, so no GitHub Actions workflow is required for Option B. If you'd rather drive the deploy from Actions (using `cloudflare/wrangler-action` and `wrangler pages deploy`), let me know and I'll add one.

---

## Option C — Stay on GitHub Pages, meta-tag CSP only

The cheap-and-quick path. Add `<meta http-equiv="Content-Security-Policy" content="...">` and `<meta name="referrer" content="...">` tags to the HTML. That's all you can do via meta.

**Effort:** ~10 minutes (but other agents are editing the HTML right now — coordinate timing).

**Result:** Observatory **B at best, often C+**. Will never reach A on GitHub Pages.

### Pros
- No vendor change, no DNS change.
- Refactor-free.

### Cons
- HSTS, X-Frame-Options, X-Content-Type-Options, Permissions-Policy, COOP/CORP **cannot be set via meta tags** — browsers explicitly ignore them there per spec. Observatory will continue to flag them as missing.
- Doesn't get you the result you asked for.

### What you do
- Add to `<head>`:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://plausible.io https://www.clarity.ms https://*.clarity.ms; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: blob: https:; connect-src 'self' https://plausible.io https://*.clarity.ms; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  ```
- That's it. Mentioned for completeness; don't pick this if you actually want A.

---

## CSP Risks — read before you deploy A or B

Skim of `static-site/index.html` and `static-site/consulting/index.html` found:

| Item | Found? | CSP impact |
|---|---|---|
| Inline `<script>` blocks (LD+JSON, Clarity bootstrap, page logic) | **Yes (7 blocks in index.html)** | Need `'unsafe-inline'` in `script-src` until refactored to nonces or external files. |
| Inline `<style>` block | **Yes (1 large block)** | Need `'unsafe-inline'` in `style-src`. Common; lots of A-grade sites still do this. |
| Inline event handlers (`onclick=`, `onload=`, etc.) | **None found** | Good — no extra allowance needed. |
| `eval()` / `new Function()` / `setTimeout("...")` | **None found** | Good — `unsafe-eval` not needed. |
| External script loads | `plausible.io/js/script.js` (active), Clarity loader (commented placeholder, will fetch from `www.clarity.ms`) | Both allow-listed in `script-src`. |
| External fonts | `fonts.googleapis.com` (CSS) + `fonts.gstatic.com` (font files) | Allow-listed in `style-src` and `font-src`. Self-hosted `/fonts/` covered by `'self'`. |
| External images | GitHub avatars, opengraph, provenance-emu.com, ifly-emu.com, icube-emu.com, ytimg, raw.githubusercontent, mono-project, retroarch.com, 9to5mac, etc. | Covered by `img-src https:`. Broad but pragmatic — there are 20+ image origins. |
| `fetch()` / XHR | **None found** | `connect-src` only needs Plausible + Clarity beacons. |
| `<iframe>` loads | None found in scan | `frame-src` not needed. |

### Active risks in the proposed CSP

1. **Clarity uses a session-replay worker that may need `worker-src` and additional `connect-src` endpoints** (`*.clarity.ms`, `c.clarity.ms`, `c.bing.com`). Already in the policy. If Clarity ever stops reporting, check the Clarity dashboard for the actual endpoints it's using and widen `connect-src` accordingly.

2. **`unsafe-inline` in `script-src`** is the one weakness in the score — Observatory **does** dock points for this and you'll likely land at A rather than A+. Getting to A+ would require refactoring all inline scripts to external files (or adding nonces, which requires a build-time step). Not in scope for this task; flagged for follow-up.

3. **`img-src https:`** is intentionally broad. The site loads images from a long tail of hand-curated sources (project icons, screenshots from emulator websites). Tightening this would mean enumerating ~15 origins and updating it every time a new project image is added. Trade-off accepted.

4. **`upgrade-insecure-requests`** is included; double-check no remaining `http://` references in HTML before going live, otherwise they'll be silently upgraded (usually fine, but worth a `grep -n 'http://' static-site/index.html` first).

5. **Plausible script** is currently loaded; the **Clarity script is commented out** in source. CSP allow-lists Clarity preemptively so when you uncomment it, nothing breaks.

---

## Recommendation

**Do Option A.** You already have a working GitHub Pages deploy that runs on push to `master`. Don't replace working infrastructure when you can stick a CDN in front of it for the same outcome in 30 minutes. Cloudflare Pages (Option B) is fine, but it's a strictly larger change (new deploy, new vendor relationship for hosting, not just for headers) for the same Observatory grade.

If you ever need to migrate off GitHub Pages later (e.g., for build-time templating, `_redirects`, or Pages Functions), Option B is there as the upgrade path — and `static-site/_headers` is already committed for that day.

---

## Files in this repo for the migration

- `MIGRATION.md` — this file.
- `cloudflare-transform-rules.json` — Transform Rules JSON for **Option A**. Also includes a Terraform snippet and a direct API equivalent.
- `static-site/_headers` — Cloudflare Pages config for **Option B**. Will be ignored by GitHub Pages (no harm in committing it now).
