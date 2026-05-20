# Deployment Notes

This repository is the root GitHub Pages repository for:

```text
https://wanghongjian98.github.io/
```

## Recommended Pages Setting

Use the included GitHub Actions workflow:

```text
Settings > Pages > Build and deployment > Source: GitHub Actions
```

Then push to `main`. The workflow in `.github/workflows/pages.yml` uploads the repository root as the Pages artifact.

## Alternative Branch Setting

If you do not use Actions, set:

```text
Settings > Pages > Build and deployment
Source: Deploy from a branch
Branch: main
Folder: /root
```

## Profile README Repository

The GitHub profile README is a different repository:

```text
wanghongjian98/wanghongjian98
```

That repository controls the README on:

```text
https://github.com/wanghongjian98
```
