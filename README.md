# Hongjian Wang Personal Website

This repository publishes the root GitHub Pages site:

```text
https://wanghongjian98.github.io/
```

The homepage is a static `index.html` page for Hongjian Wang, PhD student at ETH Zürich and member of TOMCAT at the Paul Scherrer Institute.

## Click Recorder

The homepage includes a lightweight client-side recorder for:

- Referrer/source URL
- Visit count from the current browser
- Tracked outbound link clicks

Because GitHub Pages is static hosting, the built-in recorder stores counts in `localStorage` for the current browser. To collect global counts across visitors, set the `endpoint` value in the inline tracker script to a serverless endpoint such as Cloudflare Workers, Umami, GoatCounter, or another analytics collector that accepts `navigator.sendBeacon` payloads.

## Visitor Globe

The homepage also includes a visitor globe component. GitHub Pages cannot read or store visitor IP addresses directly, so the globe needs a small backend.

This repository includes a Cloudflare Worker example:

```text
visitor-globe-worker/
```

Recommended behavior:

- Do not expose raw IP addresses in the browser.
- Use Cloudflare request metadata for approximate country/city coordinates.
- Store only aggregate counts in Workers KV.
- Use a short-lived hashed visitor id only for daily de-duplication.

After deploying the Worker, set `visitorGlobeEndpoint` in `index.html` to the Worker URL.

## Related Site

- Computational Imaging Frontier: <https://wanghongjian98.github.io/computational-imaging-frontier/>

## Deployment

This repository includes a GitHub Actions workflow at:

```text
.github/workflows/pages.yml
```

In GitHub, set:

```text
Settings > Pages > Build and deployment > Source: GitHub Actions
```

After that, every push to `main` deploys the site automatically.
