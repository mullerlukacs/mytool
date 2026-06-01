# mytool

`mytool` is a deterministic, white-hat SEO Backlink Management System that helps API and dashboard workflows evaluate backlink prospects, generate safe acquisition plans, flag toxic sources, and suggest natural anchor text.

## Input payload

Create a JSON file with these fields:

```json
{
  "website_url": "https://example.com",
  "keywords": ["content marketing", "seo strategy"],
  "niche": "marketing software",
  "competitors": ["https://competitor.example"],
  "sites_list": [
    "https://example.org/marketing/resources",
    "https://medium.com/topic/marketing",
    "https://free-backlinks-casino-pbn.example"
  ]
}
```

## CLI usage

Generate dashboard-friendly Markdown:

```bash
python seo_backlink_manager.py payload.json
```

Generate structured JSON:

```bash
python seo_backlink_manager.py payload.json --format json
```

## What the report includes

- Website niche and keyword opportunity analysis.
- Backlink source evaluation table with backlink type, relevance, score, and quality tier.
- Recommended opportunities for guest posts, Web 2.0 properties, profiles, directories, forums, resource pages, and business citations.
- Brand, URL, partial-match, and generic anchor text suggestions.
- Four-week white-hat backlink acquisition plan.
- Toxic-source and spam-indicator risk analysis.
- Content ideas designed to attract backlinks naturally.

## White-hat rules

The system is intentionally conservative. It does not recommend link schemes, automated spam, hacked sites, cloaking, private blog networks, doorway pages, or manipulative tactics. Prioritize relevance, editorial quality, and sustainable long-term SEO growth over link volume.
