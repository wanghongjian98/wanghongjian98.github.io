# Deployment Notes

There are two different GitHub surfaces:

## 1. GitHub profile README

Repository:

```text
wanghongjian98/wanghongjian98
```

This repository controls the README shown on:

```text
https://github.com/wanghongjian98
```

It does not normally control:

```text
https://wanghongjian98.github.io/
```

## 2. GitHub Pages user homepage

The root Pages homepage should be hosted by a repository named:

```text
wanghongjian98.github.io
```

The repository URL should be:

```text
https://github.com/wanghongjian98/wanghongjian98.github.io
```

To publish the root homepage:

1. Create a public repository named `wanghongjian98.github.io`.
2. Copy `index.html` and `.nojekyll` into that repository.
3. Add `images/Wang_Hongjian.jpg` if you want the portrait to render.
4. Enable GitHub Pages from `Settings > Pages`.
5. Visit `https://wanghongjian98.github.io/`.

If you enable Pages on this `wanghongjian98/wanghongjian98` repository instead, the URL will normally be:

```text
https://wanghongjian98.github.io/wanghongjian98/
```
