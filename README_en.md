# FuYouGe · Personal Blog

> Fuyou's personal blog — poetry, essays, and social links

## Online

- Domain: <https://fsg.foryoufsg.com>
- GitHub Pages: <https://hctj353056.github.io/foryoufsg-website/>

## Structure

```
foryoufsg-website/
├── index.html              # Blog homepage (poems + essays merged by date)
├── poetry/index.html       # Ancient poetry section
├── essays/index.html       # Prose section
├── social/index.html       # Social media links
├── css/style.css           # Shared styles
├── js/blog-loader.js       # Data loader & renderer
└── knowledge-base/         # Data storage
    └── original-works/
        ├── poetry/         # Poem JSON + images
        └── articles/       # Essay JSON + images
```

## Sections

| Section | Path | Description |
|---------|------|-------------|
| Blog | `/` | Merged feed of all works by date |
| Poetry | `/poetry/` | Original ancient-style poems |
| Essays | `/essays/` | Original prose |
| Social | `/social/` | External links |

## How to add content

- **Poem**: edit `knowledge-base/original-works/poetry/诗词.json`
- **Essay**: edit `knowledge-base/original-works/articles/散文.json`
- **Link**: edit `social/index.html`

## Tech

- HTML5 + CSS3
- Vanilla JavaScript (fetch + template)
- GitHub Pages

## License

Personal site, not open-source.

***

FuYou ♡

***

*FuYouGe · foryoufsg-website*
