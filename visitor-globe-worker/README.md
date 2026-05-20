# Visitor Globe Worker

This Cloudflare Worker records aggregated visit locations for:

```text
https://wanghongjian98.github.io/
```

It intentionally does not return raw IP addresses to the website. The Worker uses Cloudflare request metadata to read approximate location fields and stores aggregate counts in Workers KV.

## Deploy

1. Install Wrangler:

```powershell
npm install -g wrangler
```

2. Log in:

```powershell
wrangler login
```

3. Create a KV namespace:

```powershell
wrangler kv namespace create VISITOR_GLOBE
```

4. Create `wrangler.toml`:

```powershell
copy wrangler.toml.example wrangler.toml
```

5. Replace:

```text
replace-with-your-kv-namespace-id
replace-with-a-long-random-secret
```

6. Deploy:

```powershell
wrangler deploy
```

7. In the homepage `index.html`, set:

```js
const visitorGlobeEndpoint = "https://your-worker-name.your-subdomain.workers.dev";
```

## Endpoints

- `POST /collect`: receives a visit event and aggregates location counts.
- `GET /stats`: returns aggregated points for the globe.

## Privacy Note

IP addresses can be personal data. Prefer aggregated city/country counts and hashed short-lived visitor IDs over storing raw IP addresses. Add a short privacy notice on the website before enabling persistent analytics.
