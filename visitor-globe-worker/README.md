# Visitor Globe Worker

This Cloudflare Worker records aggregated visit locations for:

```text
https://wanghongjian98.github.io/
```

It intentionally does not store or return raw IP addresses. The Worker uses Cloudflare request metadata to read approximate location fields, hashes the IP with a daily salt only for short-lived unique-visitor counting, and stores aggregate city/country counts in Workers KV.

## Deploy

1. Install or run Wrangler:

```powershell
npx wrangler --version
```

2. Log in to Cloudflare:

```powershell
npx wrangler login
```

3. Create a KV namespace:

```powershell
npx wrangler kv namespace create VISITOR_GLOBE
```

4. Create `wrangler.toml` from the example:

```powershell
copy wrangler.toml.example wrangler.toml
```

5. Replace the placeholder KV namespace id in `wrangler.toml` with the id printed by Wrangler.

6. Store a private hash salt as a Worker secret. Do not commit this value:

```powershell
npx wrangler secret put HASH_SALT
```

Use a long random string. In PowerShell you can generate one with:

```powershell
[guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
```

7. Deploy:

```powershell
npx wrangler deploy
```

8. Copy the deployed Worker URL. In the homepage `index.html`, set:

```js
const visitorGlobeEndpoint = "https://your-worker-name.your-subdomain.workers.dev";
```

Then commit and push the homepage.

## Endpoints

- `POST /collect`: receives a visit event and aggregates location counts.
- `GET /stats`: returns aggregated points for the globe.

## Privacy Note

IP addresses can be personal data. This Worker avoids storing raw IP addresses and keeps only aggregated location counts plus short-lived daily visitor hashes. If you change it to store raw IPs, add a clear privacy notice and comply with the privacy rules that apply to your visitors.
