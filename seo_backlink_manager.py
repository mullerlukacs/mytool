"""AI-assisted SEO backlink management helpers.

This module provides a deterministic, white-hat backlink evaluation workflow that
can be used from an API, dashboard, or command line. It does not automate link
placement; it prioritizes safe planning, source qualification, anchor diversity,
and toxic-link avoidance.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable
from urllib.parse import urlparse


TOXIC_PATTERNS = {
    "casino",
    "poker",
    "betting",
    "loan",
    "payday",
    "adult",
    "porn",
    "viagra",
    "pharma",
    "escort",
    "hack",
    "crack",
    "warez",
    "free-backlinks",
    "link-farm",
    "seo-links",
    "pbn",
}

DIRECTORY_SIGNALS = {"directory", "listing", "citation", "business", "local", "chamber", "yelp"}
FORUM_SIGNALS = {"forum", "community", "answers", "quora", "reddit", "stackexchange", "discourse"}
PROFILE_SIGNALS = {"profile", "account", "author", "about", "users"}
WEB20_SIGNALS = {"medium", "wordpress", "blogspot", "tumblr", "substack", "weebly", "wix"}
RESOURCE_SIGNALS = {"resource", "resources", "links", "tools", "guide", "library", "partners"}
GUEST_POST_SIGNALS = {"write-for-us", "guest", "contribute", "submit", "blog"}
HIGH_TRUST_DOMAINS = {"edu", "gov", "org"}


@dataclass(frozen=True)
class BacklinkSourceEvaluation:
    """Quality assessment for one backlink source."""

    website: str
    type: str
    relevance: str
    score: int
    quality: str
    toxic_reasons: list[str]


@dataclass(frozen=True)
class BacklinkReport:
    """Structured report suitable for API responses and dashboards."""

    website_url: str
    niche: str
    keyword_opportunities: list[str]
    source_evaluations: list[BacklinkSourceEvaluation]
    recommended_backlinks: dict[str, list[str]]
    anchor_text_suggestions: dict[str, list[str]]
    backlink_building_plan: dict[str, list[str]]
    risk_analysis: dict[str, list[str]]
    content_ideas: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Website Analysis",
            "",
            "## Niche",
            "",
            self.niche or "General business / informational website",
            "",
            "## Keyword Opportunities",
            "",
        ]
        lines.extend(f"* {keyword}" for keyword in self.keyword_opportunities)
        lines.extend(
            [
                "",
                "# Backlink Source Evaluation",
                "",
                "| Website | Type | Relevance | Score | Quality |",
                "| ------- | ---- | --------- | ----- | ------- |",
            ]
        )
        for source in self.source_evaluations:
            lines.append(
                f"| {source.website} | {source.type} | {source.relevance} | "
                f"{source.score} | {source.quality} |"
            )

        lines.extend(["", "# Recommended Backlinks", ""])
        labels = [
            ("Guest Posts", "guest_posts"),
            ("Web 2.0", "web_2_0"),
            ("Profiles", "profiles"),
            ("Directories", "directories"),
            ("Forums", "forums"),
            ("Resource Pages", "resource_pages"),
            ("Business Citations", "business_citations"),
        ]
        for label, key in labels:
            lines.append(f"* {label}: {', '.join(self.recommended_backlinks[key]) or 'None identified'}")

        lines.extend(["", "# Anchor Text Suggestions", ""])
        for label, key in [
            ("Brand", "brand"),
            ("URL", "url"),
            ("Partial Match", "partial_match"),
            ("Generic", "generic"),
        ]:
            lines.append(f"* {label}: {', '.join(self.anchor_text_suggestions[key])}")

        lines.extend(["", "# Backlink Building Plan", ""])
        for week in ("Week 1", "Week 2", "Week 3", "Week 4"):
            lines.append(f"{week}:")
            lines.extend(f"* {item}" for item in self.backlink_building_plan[week])

        lines.extend(["", "# Risk Analysis", ""])
        for label, key in [
            ("Toxic Sources", "toxic_sources"),
            ("Spam Indicators", "spam_indicators"),
            ("Recommended Actions", "recommended_actions"),
        ]:
            lines.append(f"* {label}: {', '.join(self.risk_analysis[key]) or 'None found'}")

        lines.extend(["", "# Link-Worthy Content Ideas", ""])
        lines.extend(f"* {idea}" for idea in self.content_ideas)
        return "\n".join(lines) + "\n"


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = f"https://{url}"
    return url


def _domain_parts(url: str) -> tuple[str, str, set[str]]:
    parsed = urlparse(_normalize_url(url))
    domain = parsed.netloc.lower().removeprefix("www.")
    path_tokens = set(re.findall(r"[a-z0-9]+", parsed.path.lower()))
    domain_tokens = set(re.findall(r"[a-z0-9]+", domain))
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    return domain, tld, domain_tokens | path_tokens


def _keyword_tokens(keywords: Iterable[str], niche: str) -> set[str]:
    text = " ".join([niche, *keywords]).lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))
    stop_words = {"and", "or", "the", "for", "to", "in", "near", "best", "top", "with", "a", "an"}
    return {token for token in tokens if len(token) > 2 and token not in stop_words}


def _brand_name(website_url: str) -> str:
    domain, _, _ = _domain_parts(website_url)
    root = domain.split(".")[0] if domain else "Your Brand"
    return re.sub(r"[-_]", " ", root).title()


def _detect_type(url: str) -> str:
    domain, _, tokens = _domain_parts(url)
    token_text = " ".join(tokens | set(domain.split(".")))
    signal_map = [
        (GUEST_POST_SIGNALS, "Guest Post"),
        (WEB20_SIGNALS, "Web 2.0 Property"),
        (PROFILE_SIGNALS, "Profile Link"),
        (DIRECTORY_SIGNALS, "Directory Listing"),
        (FORUM_SIGNALS, "Forum Mention"),
        (RESOURCE_SIGNALS, "Resource Page"),
    ]
    for signals, backlink_type in signal_map:
        if signals & tokens or any(signal in token_text for signal in signals):
            return backlink_type
    return "Editorial / Contextual Opportunity"


def _toxic_reasons(url: str) -> list[str]:
    domain, _, tokens = _domain_parts(url)
    reasons: list[str] = []
    toxic_matches = sorted(TOXIC_PATTERNS & tokens)
    if toxic_matches:
        reasons.append(f"Contains spam-sensitive terms: {', '.join(toxic_matches)}")
    if len(domain) > 55:
        reasons.append("Unusually long domain can indicate a low-quality doorway or churn-and-burn site")
    if domain.count("-") >= 3:
        reasons.append("Excessive hyphenation is a common spam signal")
    if re.search(r"\d{4,}", domain):
        reasons.append("Long numeric strings in the domain may indicate generated or disposable sites")
    return reasons


def _relevance(url: str, keyword_tokens: set[str]) -> tuple[str, int]:
    _, tld, tokens = _domain_parts(url)
    overlap = keyword_tokens & tokens
    if len(overlap) >= 2:
        return "High", 30
    if len(overlap) == 1:
        return "Medium", 18
    if tld in HIGH_TRUST_DOMAINS:
        return "Medium", 12
    return "Low", 4


def evaluate_source(url: str, keywords: Iterable[str], niche: str) -> BacklinkSourceEvaluation:
    """Evaluate one possible backlink source with conservative white-hat scoring."""

    normalized_url = _normalize_url(url)
    domain, tld, _ = _domain_parts(normalized_url)
    backlink_type = _detect_type(normalized_url)
    toxic = _toxic_reasons(normalized_url)
    relevance, relevance_score = _relevance(normalized_url, _keyword_tokens(keywords, niche))

    score = 35 + relevance_score
    if backlink_type in {"Guest Post", "Resource Page", "Editorial / Contextual Opportunity"}:
        score += 14
    elif backlink_type in {"Directory Listing", "Forum Mention"}:
        score += 8
    elif backlink_type in {"Profile Link", "Web 2.0 Property"}:
        score += 4
    if tld in HIGH_TRUST_DOMAINS:
        score += 8
    if domain.startswith(("linkedin.", "medium.", "substack.", "github.")):
        score += 5
    if toxic:
        score -= 42
    score = max(1, min(100, score))

    if score >= 75:
        quality = "High Quality"
    elif score >= 50:
        quality = "Medium Quality"
    else:
        quality = "Low Quality"

    return BacklinkSourceEvaluation(
        website=normalized_url,
        type=backlink_type,
        relevance=relevance,
        score=score,
        quality=quality,
        toxic_reasons=toxic,
    )


def generate_report(
    website_url: str,
    keywords: Iterable[str] | str,
    niche: str,
    competitors: Iterable[str] | None = None,
    sites_list: Iterable[str] | None = None,
) -> BacklinkReport:
    """Generate a full backlink management report."""

    keyword_list = _coerce_list(keywords)
    competitor_list = [_normalize_url(url) for url in (competitors or []) if url]
    source_evaluations = [
        evaluate_source(site, keyword_list, niche) for site in (sites_list or []) if str(site).strip()
    ]
    brand = _brand_name(website_url)
    normalized_site = _normalize_url(website_url)
    domain, _, _ = _domain_parts(normalized_site)

    recommended = {
        "guest_posts": _select_by_type(source_evaluations, "Guest Post"),
        "web_2_0": _select_by_type(source_evaluations, "Web 2.0 Property"),
        "profiles": _select_by_type(source_evaluations, "Profile Link"),
        "directories": _select_by_type(source_evaluations, "Directory Listing"),
        "forums": _select_by_type(source_evaluations, "Forum Mention"),
        "resource_pages": _select_by_type(source_evaluations, "Resource Page"),
        "business_citations": _business_citation_suggestions(source_evaluations),
    }

    partial_match = [
        f"{keyword} guide" for keyword in keyword_list[:2]
    ] + [f"{niche} resources"] if niche else [f"{keyword} guide" for keyword in keyword_list[:3]]

    report = BacklinkReport(
        website_url=normalized_site,
        niche=_niche_analysis(niche, keyword_list, competitor_list),
        keyword_opportunities=_keyword_opportunities(keyword_list, niche),
        source_evaluations=source_evaluations,
        recommended_backlinks=recommended,
        anchor_text_suggestions={
            "brand": [brand, f"{brand} resources", f"{brand} website"],
            "url": [normalized_site, domain, f"www.{domain}" if domain else normalized_site],
            "partial_match": partial_match[:4],
            "generic": ["learn more", "visit this website", "useful resource", "read the full guide"],
        },
        backlink_building_plan=_building_plan(keyword_list, niche),
        risk_analysis=_risk_analysis(source_evaluations),
        content_ideas=_content_ideas(keyword_list, niche, competitor_list),
    )
    return report


def _coerce_list(values: Iterable[str] | str) -> list[str]:
    if isinstance(values, str):
        return [item.strip() for item in re.split(r"[,\n]", values) if item.strip()]
    return [str(item).strip() for item in values if str(item).strip()]


def _select_by_type(evaluations: list[BacklinkSourceEvaluation], backlink_type: str) -> list[str]:
    return [
        source.website
        for source in evaluations
        if source.type == backlink_type and source.quality != "Low Quality" and not source.toxic_reasons
    ][:5]


def _business_citation_suggestions(evaluations: list[BacklinkSourceEvaluation]) -> list[str]:
    citations = [
        source.website
        for source in evaluations
        if source.type == "Directory Listing" and source.score >= 55 and not source.toxic_reasons
    ]
    return citations[:5]


def _niche_analysis(niche: str, keywords: list[str], competitors: list[str]) -> str:
    niche_text = niche or "the target market"
    keyword_text = ", ".join(keywords[:5]) if keywords else "core commercial and informational queries"
    competitor_text = f" Competitors reviewed: {', '.join(competitors[:3])}." if competitors else ""
    return (
        f"The website operates in {niche_text}. Backlink acquisition should emphasize topical "
        f"authority around {keyword_text}, prioritizing editorial placements, reputable niche "
        f"directories, resource pages, and genuine community mentions over raw link volume."
        f"{competitor_text}"
    )


def _keyword_opportunities(keywords: list[str], niche: str) -> list[str]:
    if not keywords:
        return [
            f"Build topic clusters around {niche or 'the primary niche'} pain points",
            "Create informational assets that earn editorial citations",
            "Target local and industry-specific citation opportunities",
        ]
    return [
        f"Create link-worthy informational content for '{keyword}'"
        for keyword in keywords[:6]
    ] + ["Use competitor gap analysis to find relevant resource-page and guest-post prospects"]


def _building_plan(keywords: list[str], niche: str) -> dict[str, list[str]]:
    topic = niche or (keywords[0] if keywords else "the niche")
    return {
        "Week 1": [
            "Audit existing backlinks and disavow only clearly harmful links after manual review.",
            f"Finalize a prospect list of relevant {topic} publications, associations, and directories.",
            "Prepare brand, URL, generic, and partial-match anchor text guidelines.",
        ],
        "Week 2": [
            "Claim or improve legitimate business profiles and citation listings.",
            "Pitch 3-5 highly relevant guest post or expert quote opportunities.",
            "Publish one link-worthy informational asset on the website.",
        ],
        "Week 3": [
            "Request inclusion on resource pages where the content genuinely improves the page.",
            "Participate in niche forums or communities with helpful, non-promotional answers.",
            "Build relationships with journalists, bloggers, and industry newsletter editors.",
        ],
        "Week 4": [
            "Review new links for indexability, relevance, and anchor diversity.",
            "Refresh outreach messaging based on reply rates and editorial feedback.",
            "Plan the next content-led campaign using topics that attracted engagement.",
        ],
    }


def _risk_analysis(evaluations: list[BacklinkSourceEvaluation]) -> dict[str, list[str]]:
    toxic_sources = [source.website for source in evaluations if source.toxic_reasons]
    spam_indicators = sorted({reason for source in evaluations for reason in source.toxic_reasons})
    return {
        "toxic_sources": toxic_sources,
        "spam_indicators": spam_indicators,
        "recommended_actions": [
            "Avoid paid link schemes, automated profile creation, private blog networks, hacked placements, and doorway pages.",
            "Manually review low-quality sources before outreach and prioritize relevance, editorial standards, and real traffic.",
            "Maintain a natural anchor mix dominated by brand, URL, and generic anchors.",
        ],
    }


def _content_ideas(keywords: list[str], niche: str, competitors: list[str]) -> list[str]:
    base_topic = niche or (keywords[0] if keywords else "your industry")
    ideas = [
        f"Original data study: benchmarks and trends in {base_topic}",
        f"Definitive beginner-to-advanced guide for {keywords[0] if keywords else base_topic}",
        f"Expert roundup answering common {base_topic} questions",
        f"Free checklist, calculator, or template for {base_topic} audiences",
        "Comparison page that explains options transparently without attacking competitors",
    ]
    if competitors:
        ideas.append("Competitor gap resource that covers unanswered questions found on competing sites")
    return ideas


def _load_payload(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a white-hat SEO backlink management report.")
    parser.add_argument("payload", help="Path to a JSON payload containing website_url, keywords, niche, competitors, and sites_list.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    payload = _load_payload(args.payload)
    report = generate_report(
        website_url=payload.get("website_url", ""),
        keywords=payload.get("keywords", []),
        niche=payload.get("niche", ""),
        competitors=payload.get("competitors", []),
        sites_list=payload.get("sites_list", []),
    )
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_markdown())


if __name__ == "__main__":
    main()
