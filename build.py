#!/usr/bin/env python3
"""Generate the portfolio's static pages.

The shared layout (head, top nav, footer) lives in this file, page bodies live in
src/pages/*.html and data lives in content/*.json. After editing any of them run

    python3 build.py

(or `python3 build.py --watch` to rebuild on every save while previewing)
and commit the generated HTML: GitHub Pages serves it as-is, with no build of its own.
Standard library only, no dependencies.

Templates use {{ name }} placeholders, filled from each page's context. An unknown
name stops the build, so typos can't ship.
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES_DIR = ROOT / "src" / "pages"
CONTENT_DIR = ROOT / "content"

SITE_URL = "https://shakiz.github.io"
GA_ID = "G-JNXBMHBRCS"

LINKS = {
    "linkedin": "https://www.linkedin.com/in/sakhawat-hossain-762688127/",
    "github": "https://github.com/shakiz",
    "medium": "https://shakilbd.medium.com/",
    "stackoverflow": "https://stackoverflow.com/users/10603313/sakhawat-hossain",
    "booking": "https://cal.com/sakhawat",
    "youtube": "",  # Empty hides the YouTube strip on /writing/. Add the channel URL to show it.
}

EMAIL = "shakil.py@gmail.com"

# The resume Google Doc linked from the old site, exported as PDF.
RESUME_PDF = "https://docs.google.com/document/d/1ylyxfAczwnSyKtxlY9bLduZ-VCyAmXGSfgOuMoCrOBs/export?format=pdf"

# Contact form backend. Set to a Formspree endpoint (https://formspree.io/f/<id>) to
# send messages from the page. Empty falls back to opening the visitor's email app.
FORM_ENDPOINT = ""

# (label, href, key). A page whose `active` matches the key gets aria-current.
NAV = [
    ("Career", "/#career", None),
    ("Leadership", "/#leadership", None),
    ("Work", "/work/", "work"),
    ("Guides", "/guides/", "guides"),
    ("Writing", "/writing/", "writing"),
    ("Resume", "/resume/", "resume"),
]

FOOTER_LINKS = [
    ("Work", "/work/"),
    ("Guides", "/guides/"),
    ("Writing", "/writing/"),
    ("Resume", "/resume/"),
    ("Contact", "/contact/"),
    ("LinkedIn", LINKS["linkedin"]),
    ("GitHub", LINKS["github"]),
]

# Brand icons (24×24 paths from Simple Icons, CC0) for icon-only social links.
SOCIAL_ICONS = {
    "linkedin": ("LinkedIn", "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"),
    "github": ("GitHub", "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"),
    "medium": ("Medium", "M13.54 12a6.8 6.8 0 0 1-6.77 6.82A6.8 6.8 0 0 1 0 12a6.8 6.8 0 0 1 6.77-6.82A6.8 6.8 0 0 1 13.54 12zm7.42 0c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z"),
    "stackoverflow": ("Stack Overflow", "M15.725 0l-1.72 1.277 6.39 8.588 1.716-1.277L15.725 0zm-3.94 3.418l-1.369 1.644 8.225 6.85 1.369-1.644-8.225-6.85zm-3.15 4.465l-.905 1.94 9.702 4.517.904-1.94-9.701-4.517zm-1.85 4.86l-.44 2.093 10.473 2.201.44-2.092-10.473-2.203zM1.89 15.47V24h19.19v-8.53h-2.133v6.397H4.021v-6.396H1.89zm4.265 2.133v2.13h10.66v-2.13H6.154z"),
}


def social_icon_links(keys):
    """Icon-only links; the name is the accessible label and the hover tooltip."""
    links = []
    for key in keys:
        name, path = SOCIAL_ICONS[key]
        links.append(
            f'<a {link_attrs(LINKS[key])} aria-label="{name}" title="{name}">'
            f'<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="{path}"/></svg></a>'
        )
    return "\n\t\t\t\t".join(links)


# Short topic names used in compact post metadata ("Compose · Apr 2026").
TOPIC_SHORT = {
    "android": "Android",
    "compose": "Compose",
    "kotlin": "Kotlin",
    "xp": "Cross‑platform",
}

PLACEHOLDER = re.compile(r"\[[^\]]+\]")


# ---------- helpers ----------

def esc(value):
    return html.escape(str(value), quote=True)


def todo_comment(note):
    # "--" is not allowed inside an HTML comment.
    return f"<!-- TODO: {note.replace('--', '- -')} -->"


def text(value):
    """Escape a content string for a text node. Any [bracketed] placeholder stays
    visible and gets a TODO comment next to it, so it's easy to find with grep."""
    out = esc(value)
    found = PLACEHOLDER.findall(value)
    if found:
        out += " " + todo_comment("replace placeholder " + ", ".join(found))
    return out


def external(href):
    return href.startswith("http")


def link_attrs(href):
    """href plus rel/target for links that leave the site."""
    attrs = f'href="{esc(href)}"'
    if external(href):
        attrs += ' target="_blank" rel="noopener"'
    return attrs


def load_json(name):
    with open(CONTENT_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def render_template(path, context):
    source = path.read_text(encoding="utf-8")

    def substitute(match):
        key = match.group(1)
        if key not in context:
            sys.exit(f"{path.relative_to(ROOT)}: unknown placeholder {{{{ {key} }}}}")
        return str(context[key])

    return re.sub(r"\{\{\s*([a-z0-9_]+)\s*\}\}", substitute, source)


# ---------- shared components ----------

def top_nav(active):
    brand_current = ' aria-current="page"' if active == "home" else ""
    links = []
    for label, href, key in NAV:
        current = ' aria-current="page"' if key and key == active else ""
        links.append(f'<a class="nav__link" href="{href}"{current}>{label}</a>')
    contact_current = ' aria-current="page"' if active == "contact" else ""
    links.append(f'<a class="btn btn--primary btn--sm" href="/contact/"{contact_current}>Contact</a>')
    joined = "\n\t\t\t\t".join(links)
    return f"""<header class="site-header">
	<nav class="container nav" aria-label="Primary">
		<a class="nav__brand" href="/"{brand_current}>Sakhawat<span class="nav__brand-role"> / mobile lead</span></a>
		<div class="nav__links">
				{joined}
		</div>
		<button type="button" class="menu-toggle" aria-expanded="false" aria-controls="site-menu" aria-label="Open menu">
			<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 8h16"/><path d="M4 16h16"/></svg>
		</button>
	</nav>
</header>
{mobile_menu(active)}"""


# Full-screen menu used below 880px. Opened by .menu-toggle, see js/site.js.
MENU_LINKS = [
    ("Home", "/", "home"),
    ("Career", "/#career", None),
    ("Work", "/work/", "work"),
    ("Guides", "/guides/", "guides"),
    ("Writing", "/writing/", "writing"),
    ("Resume", "/resume/", "resume"),
]


def mobile_menu(active):
    links = []
    for i, (label, href, key) in enumerate(MENU_LINKS):
        current = ' aria-current="page"' if key and key == active else ""
        links.append(f'<a href="{href}"{current}>{label}<span class="menu__num" aria-hidden="true">{i}</span></a>')
    joined = "\n\t\t".join(links)
    return f"""<div class="menu" id="site-menu" role="dialog" aria-modal="true" aria-label="Site menu" hidden>
	<div class="menu__bar">
		<a class="nav__brand" href="/">Sakhawat<span class="nav__brand-role"> / mobile lead</span></a>
		<button type="button" class="menu-toggle" data-menu-close aria-label="Close menu">
			<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12"/><path d="M18 6 6 18"/></svg>
		</button>
	</div>
	<nav class="menu__links" aria-label="Menu">
		{joined}
	</nav>
	<div class="menu__extra">
		<a class="btn btn--primary btn--block" href="/contact/">Contact</a>
		<p class="status-pill"><span class="status-pill__dot" aria-hidden="true"></span>Open to opportunities</p>
		<div class="social-links">
			<a {link_attrs(LINKS["linkedin"])}>LinkedIn</a>
			<a {link_attrs(LINKS["github"])}>GitHub</a>
			<a {link_attrs(LINKS["medium"])}>Medium</a>
		</div>
	</div>
</div>"""


def footer():
    links = "\n\t\t\t".join(f"<a {link_attrs(href)}>{label}</a>" for label, href in FOOTER_LINKS)
    return f"""<footer class="site-footer">
	<div class="container footer">
		<p>© {date.today().year} Sakhawat Hossain</p>
		<div class="footer__links">
			{links}
		</div>
	</div>
</footer>"""


def layout(*, title, description, path, active, body, source,
           og_image="/images/portrait.jpg", head_extra=""):
    return f"""<!doctype html>
<!-- Generated by build.py from {source}. Edit that file and run `python3 build.py`. -->
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{esc(title)}</title>
	<script>document.documentElement.classList.add('js')</script>
	<meta name="description" content="{esc(description)}">
	<meta name="author" content="Sakhawat Hossain">
	<link rel="canonical" href="{SITE_URL}{path}">

	<meta property="og:type" content="website">
	<meta property="og:site_name" content="Sakhawat Hossain">
	<meta property="og:title" content="{esc(title)}">
	<meta property="og:description" content="{esc(description)}">
	<meta property="og:url" content="{SITE_URL}{path}">
	<meta property="og:image" content="{SITE_URL}{og_image}">
	<meta name="twitter:card" content="summary">

	<link rel="icon" type="image/png" href="/favicon.png">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&amp;family=Geist+Mono:wght@400;500&amp;display=swap">
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&amp;family=Geist+Mono:wght@400;500&amp;display=swap">
	<link rel="stylesheet" href="/css/site.css">
{head_extra}
	<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
	<script>
		window.dataLayer = window.dataLayer || [];
		function gtag() {{ dataLayer.push(arguments); }}
		gtag('js', new Date());
		gtag('config', '{GA_ID}');
	</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{top_nav(active)}
{body}
{footer()}
<script src="/js/site.js" defer></script>
</body>
</html>
"""


# ---------- page builders ----------

def home_context(projects, posts, guides):
    latest = posts[0]  # posts.json is newest first
    latest_html = f"""<a class="latest-row" {link_attrs(latest["url"])}>
			<span><span class="latest-row__label">Latest article</span><span class="latest-row__title">{text(latest["title"])}</span></span>
			<span class="latest-row__date">{esc(latest["date"])}</span>
		</a>"""

    return {
        "social_icons": social_icon_links(["linkedin", "github", "medium", "stackoverflow"]),
        "project_count": len(projects),
        "post_count": len(posts),
        "guide_count": len(guides),
        "latest_post": latest_html,
    }


# (key, label, short label for phones)
PROJECT_FILTERS = [
    ("all", "All", "All"),
    ("client", "Client products", "Client"),
    ("indie", "Indie & open source", "Indie"),
]


def responsive_text(long, short):
    """Long text from 640px up, short text on phones (see .dsk / .mob in site.css)."""
    if long == short:
        return esc(long)
    return f'<span class="dsk">{esc(long)}</span><span class="mob">{esc(short)}</span>'

# Shown instead of screenshots for projects without an image (e.g. under NDA).
NO_IMAGE_TEXT = "[Screens under NDA — add an architecture sketch]"


def project_media(project, css_class, lazy):
    if not project["image"]:
        return f'<div class="media media-placeholder {css_class}">{text(NO_IMAGE_TEXT)}</div>'
    loading = ' loading="lazy" decoding="async"' if lazy else ""
    return (f'<img class="media {css_class}" src="{esc(project["image"])}" width="1272" height="477"'
            f' alt="{esc(project.get("imageAlt") or project["name"] + " app screens")}"{loading}>')


def filter_chips(filters, counts):
    chips = []
    for key, label, short in filters:
        pressed = "true" if key == "all" else "false"
        chips.append(f'<button type="button" class="chip" data-filter="{key}" aria-pressed="{pressed}">'
                     f'{responsive_text(label, short)} <span class="chip__count">{counts.get(key, 0)}</span></button>')
    return "\n\t\t\t".join(chips)


def work_context(projects):
    counts = {"all": len(projects)}
    for p in projects:
        counts[p["category"]] = counts.get(p["category"], 0) + 1

    cards = []
    for i, p in enumerate(projects):
        cards.append(f"""<a class="card project-card" href="/work/{p["slug"]}/" data-filter-tags="{esc(p["category"])}">
				{project_media(p, "", lazy=i >= 2)}
				<div class="project-card__body">
					<p class="project-card__meta">{text(p["cardMeta"])}</p>
					<h2 class="project-card__name">{text(p["name"])}</h2>
					<p class="project-card__summary">{text(p["summary"])}</p>
					<div class="project-card__footer">
						<div class="tag-list dsk">
							<span class="tag">{text(p["role"])}</span>
							<span class="tag">{text(p["platform"])}</span>
						</div>
						<span class="project-card__line mob">{esc(p["role"])} · {esc(p["platform"])}</span>
						<span class="project-card__cta"><span class="dsk">View project </span>→</span>
					</div>
				</div>
			</a>""")

    return {
        "filter_chips": filter_chips(PROJECT_FILTERS, counts),
        "project_cards": "\n\t\t\t".join(cards),
    }


def project_context(projects, index):
    p = projects[index]
    n = len(projects)
    prev_p = projects[(index - 1) % n]
    next_p = projects[(index + 1) % n]

    owned = "\n\t\t\t\t\t".join(
        f'<li><span class="arrow-list__mark" aria-hidden="true">→</span><span>{text(item)}</span></li>'
        for item in p["owned"]
    )
    impact = "\n\t\t\t\t".join(
        f'<div><p class="stat__value">{text(s["value"])}</p><p class="stat__label">{text(s["label"])}</p></div>'
        for s in p["impact"]
    )
    stack = "\n\t\t\t\t\t".join(f'<span class="tag">{text(t)}</span>' for t in p["stack"])

    return {
        "position": f"{index + 1} / {n}",
        "prev_href": f"/work/{prev_p['slug']}/",
        "prev_name": esc(prev_p["name"]),
        "next_href": f"/work/{next_p['slug']}/",
        "next_name": esc(next_p["name"]),
        "tag": text(p["tag"]),
        "name": text(p["name"]),
        "summary": text(p["summary"]),
        "media": project_media(p, "detail-media", lazy=False),
        "role": text(p["role"]),
        "client": text(p["client"]),
        "timeline": text(p["timeline"]),
        "platform": text(p["platformDetail"]),
        "overview": text(p["overview"]),
        "owned": owned,
        # Optional: leave "keyDecision" out of projects.json to hide the box.
        "key_decision": (f"""<section class="callout">
				<h2 class="callout__label">Key decision</h2>
				<p class="callout__text">{text(p["keyDecision"])}</p>
			</section>""" if p.get("keyDecision") else ""),
        "impact": impact,
        "stack": stack,
        "ctas": project_ctas(p["cta"]),
    }


def project_ctas(cta):
    """A project's `cta` is one {label, href} or a list of them (e.g. Google Play and
    App Store). The first is the primary button, the rest are outline buttons."""
    links = cta if isinstance(cta, list) else [cta]
    buttons = []
    for i, link in enumerate(links):
        style = "btn--primary" if i == 0 else "btn--secondary"
        buttons.append(f'<a class="btn {style} btn--block" {link_attrs(link["href"])}>{esc(link["label"])} →</a>')
    return "\n\t\t\t\t".join(buttons)


WRITING_FILTERS = [
    ("all", "All", "All"),
    ("compose", "Jetpack Compose", "Compose"),
    ("kotlin", "Kotlin", "Kotlin"),
    ("xp", "Cross‑platform", "Cross‑platform"),
    ("android", "Android platform", "Android"),
]


def writing_context(posts):
    counts = {"all": len(posts)}
    for p in posts:
        counts[p["topicKey"]] = counts.get(p["topicKey"], 0) + 1

    featured = next(p for p in posts if p.get("featured"))
    label = featured.get("featuredLabel") or featured["topic"]
    summary = featured.get("featuredSummary", "")
    summary_html = f'\n\t\t\t<p class="post-hero__summary dsk">{text(summary)}</p>' if summary else ""
    featured_html = f"""<a class="card post-hero" {link_attrs(featured["url"])}>
		<div class="post-hero__text">
			<p class="post-feature__label">Featured · {esc(label)}<span class="dsk"> · {esc(featured["date"])}</span></p>
			<p class="post-hero__title">{text(featured["title"])}</p>{summary_html}
		</div>
		<span class="post-hero__cta">Read article →</span>
	</a>"""

    rows = "\n\t\t\t".join(
        f"""<a class="article-row" {link_attrs(p["url"])} data-filter-tags="{esc(p["topicKey"])}">
				<span class="article-row__date">{esc(p["date"])}</span>
				<span class="article-row__title">{text(p["title"])}</span>
				<span class="article-row__tag">{esc(p["topic"])}</span>
			</a>"""
        for p in posts
    )

    # The YouTube strip only appears once LINKS["youtube"] is set.
    youtube = ""
    if LINKS["youtube"]:
        youtube = f"""<section class="strip" aria-label="Video">
		<p><span class="dsk">Prefer video? I explain AI and mobile tooling in Bangla.</span><span class="mob">Bangla videos on YouTube</span></p>
		<a class="link-arrow" {link_attrs(LINKS["youtube"])}><span><span class="dsk">Watch on YouTube </span>→</span></a>
	</section>"""

    return {
        "post_count": len(posts),
        "featured": featured_html,
        "filter_chips": filter_chips(WRITING_FILTERS, counts),
        "rows": rows,
        "youtube_strip": youtube,
    }


def contact_context():
    if FORM_ENDPOINT:
        action, enctype, form_todo = FORM_ENDPOINT, "", ""
    else:
        # Without JS the browser hands the form to the visitor's email app.
        action, enctype = f"mailto:{EMAIL}", ' enctype="text/plain"'
        form_todo = todo_comment("no form backend yet; set FORM_ENDPOINT in build.py (TODO.md)")
    return {
        "email": EMAIL,
        "link_booking": LINKS["booking"],
        "link_linkedin": LINKS["linkedin"],
        "link_github": LINKS["github"],
        "form_action": esc(action),
        "form_enctype": enctype,
        "form_endpoint": esc(FORM_ENDPOINT),
        "form_todo": form_todo,
    }


# Guide tracks: (key, eyebrow number, name, short name for phones, tagline, topics)
GUIDE_TRACKS = [
    ("agentic", "Track 01", "Agentic engineering", "Agentic",
     "Build smarter. Ship faster.", "Claude Code · context · tokens"),
    ("mobile", "Track 02", "Mobile engineering", "Mobile",
     "Ship native. Scale cross‑platform.", "Android · KMP · Flutter"),
]


def guide_card(guide):
    return f"""<a class="card guide-card" href="{esc(guide["url"])}">
					<span class="guide-card__cover">
						<span class="guide-card__stat"><span class="guide-card__big">{esc(guide["big"])}</span><span class="guide-card__unit">{esc(guide["unit"])}</span></span>
						<span class="guide-card__fmt">{esc(guide["fmt"])}</span>
					</span>
					<span class="guide-card__body">
						<span class="guide-card__tags">{esc(guide["tags"])}</span>
						<span class="guide-card__title">{esc(guide["title"])}</span>
						<span class="guide-card__line">{esc(guide["line"])}</span>
						<span class="guide-card__cta">Open guide ↗</span>
					</span>
				</a>"""


def guides_context(guides):
    counts = {"all": len(guides)}
    for g in guides:
        counts[g["t"]] = counts.get(g["t"], 0) + 1
    filters = [("all", "All", "All")] + [(key, name, short) for key, _, name, short, _, _ in GUIDE_TRACKS]

    featured = next(g for g in guides if g.get("featured"))
    track_name = next(name for key, _, name, _, _, _ in GUIDE_TRACKS if key == featured["t"])
    stats = "".join(
        f'<div class="guide-feature__stat"><p class="guide-feature__big">{esc(v)}</p><p class="guide-feature__unit">{esc(u)}</p></div>'
        for v, u in featured["featuredStats"]
    )
    featured_html = f"""<a class="card guide-feature" href="{esc(featured["url"])}">
		<div class="guide-feature__stats">{stats}</div>
		<div class="guide-feature__text">
			<p class="guide-feature__label">Featured<span class="dsk"> · {esc(track_name)}</span></p>
			<p class="guide-feature__title">{esc(featured["title"])}</p>
			<p class="guide-feature__line dsk">{esc(featured["line"])}</p>
		</div>
		<span class="guide-card__cta">Open guide ↗</span>
	</a>"""

    sections = []
    for key, number, name, short, tagline, topics in GUIDE_TRACKS:
        cards = "\n\t\t\t\t".join(guide_card(g) for g in guides if g["t"] == key)
        sections.append(f"""<section class="track" id="track-{key}" data-filter-tags="{key}" aria-labelledby="track-{key}-h">
			<div class="track__head">
				<div class="section-head__titles">
					<p class="eyebrow">{number} · {responsive_text(name, short)}</p>
					<h2 class="track__title" id="track-{key}-h">{esc(tagline)}</h2>
				</div>
				<p class="track__topics dsk">{esc(topics)}</p>
			</div>
			<div class="guide-grid">
				{cards}
			</div>
		</section>""")

    return {
        "guide_count": len(guides),
        "featured": featured_html,
        "filter_chips": filter_chips(filters, counts),
        "tracks": "\n\t\t".join(sections),
    }


def redirect_page(target, title):
    """Static stand-in for a server redirect (GitHub Pages has none)."""
    return f"""<!doctype html>
<!-- Generated by build.py: legacy URL, redirects to {target}. -->
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{esc(title)} · Sakhawat Hossain</title>
	<meta name="robots" content="noindex">
	<link rel="canonical" href="{SITE_URL}{target}">
	<meta http-equiv="refresh" content="0; url={target}">
	<script>location.replace({json.dumps(target)});</script>
</head>
<body>
	<p>This page has moved to <a href="{target}">{SITE_URL}{target}</a>.</p>
</body>
</html>
"""


def sitemap(pages, extra_paths=()):
    paths = [p["path"] for p in pages if not p.get("noindex")] + list(extra_paths)
    urls = "\n".join(f"\t<url><loc>{SITE_URL}{path}</loc></url>" for path in paths)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by build.py. Lists the portfolio pages and the guides. -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


def person_json_ld():
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Sakhawat Hossain",
        "jobTitle": "Senior Software Engineer",
        "worksFor": {"@type": "Organization", "name": "Cefalo"},
        "url": SITE_URL + "/",
        "image": SITE_URL + "/images/portrait.jpg",
        "sameAs": [LINKS["linkedin"], LINKS["github"], LINKS["medium"], LINKS["stackoverflow"]],
        "knowsAbout": ["Android", "Kotlin", "Jetpack Compose", "Kotlin Multiplatform", "Flutter", "Mobile architecture"],
    }
    return f'\t<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def build():
    projects = load_json("projects.json")
    posts = load_json("posts.json")
    guides = load_json("guides.json")

    pages = [
        {
            "source": "src/pages/home.html",
            "out": "index.html",
            "path": "/",
            "active": "home",
            "title": "Sakhawat Hossain · Mobile lead",
            "description": "Sakhawat Hossain, mobile lead and Senior Software Engineer at Cefalo. "
                           "8+ years building Android and Flutter apps in fintech, telecom and edtech.",
            "context": home_context(projects, posts, guides),
            "head_extra": person_json_ld(),
        },
        {
            "source": "src/pages/work.html",
            "out": "work/index.html",
            "path": "/work/",
            "active": "work",
            "title": "Work · Sakhawat Hossain",
            "description": "Mobile products Sakhawat Hossain has led, owned and built, from fintech "
                           "and telecom super-apps to indie and open-source Android apps.",
            "context": work_context(projects),
        },
        {
            "source": "src/pages/guides.html",
            "out": "guides/index.html",
            "path": "/guides/",
            "active": "guides",
            "title": "Guides · Sakhawat Hossain",
            "description": "Interactive guides by Sakhawat Hossain on agentic AI engineering with "
                           "Claude Code, and on Android and Flutter mobile engineering.",
            "context": guides_context(guides),
        },
        {
            "source": "src/pages/writing.html",
            "out": "writing/index.html",
            "path": "/writing/",
            "active": "writing",
            "title": "Writing · Sakhawat Hossain",
            "description": "Articles by Sakhawat Hossain on Jetpack Compose, Kotlin, "
                           "cross-platform development and the Android platform.",
            "context": writing_context(posts),
        },
        {
            "source": "src/pages/resume.html",
            "out": "resume/index.html",
            "path": "/resume/",
            "active": "resume",
            "title": "Resume · Sakhawat Hossain",
            "description": "Resume of Sakhawat Hossain, mobile lead with 8+ years shipping Android "
                           "and cross-platform apps in fintech, telecom and edtech.",
            "context": {"resume_pdf": RESUME_PDF},
        },
        {
            "source": "src/pages/contact.html",
            "out": "contact/index.html",
            "path": "/contact/",
            "active": "contact",
            "title": "Contact · Sakhawat Hossain",
            "description": "Get in touch with Sakhawat Hossain about lead and staff mobile roles, "
                           "projects, talks or mentoring.",
            "context": contact_context(),
        },
        {
            "source": "src/pages/404.html",
            "out": "404.html",
            "path": "/404.html",
            "active": None,
            "title": "Page not found · Sakhawat Hossain",
            "description": "This page doesn't exist.",
            "context": {},
            "noindex": True,
            "head_extra": '\t<meta name="robots" content="noindex">',
        },
    ]

    for i, p in enumerate(projects):
        pages.append({
            "source": "src/pages/project.html",
            "out": f"work/{p['slug']}/index.html",
            "path": f"/work/{p['slug']}/",
            "active": "work",
            "title": f"{p['name']} · Sakhawat Hossain",
            "description": p["summary"],
            "og_image": p["image"] or "/images/portrait.jpg",
            "context": project_context(projects, i),
        })

    for page in pages:
        body = render_template(ROOT / page["source"], page["context"])
        output = layout(
            title=page["title"],
            description=page["description"],
            path=page["path"],
            active=page["active"],
            body=body.rstrip("\n"),
            source=page["source"],
            og_image=page.get("og_image", "/images/portrait.jpg"),
            head_extra=page.get("head_extra", ""),
        )
        out_path = ROOT / page["out"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"wrote {page['out']}")

    # The old hub pages now redirect to the matching Guides track.
    for out, track, title in [("agentic_dev.html", "agentic", "Agentic engineering guides"),
                              ("mobile_dev.html", "mobile", "Mobile engineering guides")]:
        (ROOT / out).write_text(redirect_page(f"/guides/?track={track}", title), encoding="utf-8")
        print(f"wrote {out} (redirect)")

    (ROOT / "sitemap.xml").write_text(sitemap(pages, [g["url"] for g in guides]), encoding="utf-8")
    print("wrote sitemap.xml")


def watch():
    """Rebuild whenever a template or content file changes. Polls, so no dependencies.
    If build.py itself changes, the process restarts so the new code is used."""
    import os
    import time

    def snapshot():
        files = list((ROOT / "src").rglob("*")) + list(CONTENT_DIR.rglob("*"))
        return {f: f.stat().st_mtime for f in files if f.is_file()}

    def safe_build():
        try:
            build()
        except SystemExit as error:  # a template error; keep watching
            print(f"build failed: {error}")
        except Exception as error:  # e.g. invalid JSON while mid-edit
            print(f"build failed: {error!r}")

    script = Path(__file__).resolve()
    script_mtime = script.stat().st_mtime
    safe_build()
    seen = snapshot()
    print("watching src/ and content/ for changes (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(0.5)
            if script.stat().st_mtime != script_mtime:
                print("build.py changed, restarting")
                os.execv(sys.executable, [sys.executable, str(script), "--watch"])
            current = snapshot()
            if current != seen:
                seen = current
                print(time.strftime("%H:%M:%S"), "change detected, rebuilding")
                safe_build()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch()
    else:
        build()
