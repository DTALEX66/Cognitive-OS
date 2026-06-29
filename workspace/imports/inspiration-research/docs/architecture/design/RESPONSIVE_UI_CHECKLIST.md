# Responsive UI Checklist

## Required breakpoints

```text
Desktop: 1440px reference layout
Tablet: 960px stacked cards and route panels
Mobile: 720px single-column flow
```

## Required checks

- Top navigation does not overflow.
- Language switch remains visible near the top-right controls.
- Route cards stack cleanly.
- Timeline cards remain readable.
- Training answer area remains usable on narrow screens.
- Report KPI cards wrap without truncating key values.
- Community route cards preserve trust labels and fact-change warnings.

## Current v3.0 status

Responsive CSS markers are present and covered by `npm run validate:responsive`. Full visual screenshot review is planned for v0.8.
