# QariAI Landing Page

The marketing and content site for [QariAI](https://qariai.app) — an AI-powered Quran recitation coach that gives real-time Tajweed feedback and tracks Hifz (memorization) progress.

This repository is the **static landing/content site**, not the QariAI app itself. It's what people see at qariai.app before downloading the app.

🌐 **Live site:** https://qariai.app
📱 **The app:** [Google Play](https://play.google.com/store/apps/details?id=app.qari.ai)
📧 **Contact:** [salam@qariai.app](mailto:salam@qariai.app)

---

## What QariAI (the app) does

- **Real-time Tajweed analysis** — detects mistakes in Makharij (articulation points), Ghunnah, Madd, Qalqalah, and other Tajweed rules from live audio
- **Hifz Companion** — spaced-repetition memorization tracking with a word-level heatmap of recurring mistakes
- **Separate scoring** for Tajweed accuracy and Hifz memory accuracy, rather than one blended score
- Built on Google Gemini for audio analysis

## What's in this repository

Plain static HTML — no build step, no framework, no `npm install`. Pages are deployed directly to Vercel from this repo.

```
landing-page/
├── index.html                      # Homepage
├── academy/                        # Educational articles (Tajweed, Hifz, AI-vs-teacher, etc.)
├── qaef.html                       # Quranic AI Evaluation Framework — open methodology
│                                    #   for benchmarking Quran-recitation AI tools
├── *.html                          # Individual SEO/content pages (comparisons, guides, tools)
├── ar/, fr/, ms/                   # Translated pages
├── robots.txt                      # Includes an explicit Content-Signal AI opt-in
│                                    #   (search=yes, ai-input=yes, ai-train=yes)
├── sitemap.xml
└── vercel.json                     # URL rewrites (clean paths → .html files)
```

## Open Evaluation Methodology (QAEF)

QariAI publishes an open, reproducible methodology for evaluating AI Quranic recitation tools — including itself — across phoneme accuracy, Tajweed rule detection, timing/prosody, feedback quality, and demographic robustness. See [`/qaef`](https://qariai.app/qaef) and the full [methodology document](https://qariai.app/open-methodology).

QariAI is transparent that it is both the publisher and a subject of this methodology, and commits to publishing its own scores — including where it falls short — using the same tests applied to competitors.

## Infrastructure

- **Hosting:** Vercel
- **DNS/CDN:** Cloudflare
- **No build tooling** — HTML/CSS/JS is authored and deployed directly

## Contributing / Issues

This is a solo-maintained project. Open an issue for bugs or suggestions on the site content.

## License

© QariAI. Content and code in this repository are proprietary unless otherwise noted.
