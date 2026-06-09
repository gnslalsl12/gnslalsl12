#!/usr/bin/env python3
"""Generate the frosted-glass GitHub overview panel (assets/github.svg).

Runs in CI (see .github/workflows/stats.yml) to keep the stats fresh.
Pulls live data from the GitHub REST API when a token / network is available,
otherwise falls back to the last known values so the SVG is always valid.
"""
import os, json, datetime, urllib.request, urllib.error

USER = "gnslalsl12"
FONT = ("'Segoe UI','Montserrat',system-ui,-apple-system,"
        "'Apple SD Gothic Neo','Malgun Gothic',sans-serif")

# editorial (not derivable from the API)
FEATURED = 4
LIVE = "famring.co.kr"

# GitHub linguist-ish colors (lightened a touch where needed for white bg)
LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#e8b400", "Java": "#b07219",
    "SCSS": "#c6538c", "CSS": "#563d7c", "HTML": "#e34c26", "C#": "#178600",
    "Python": "#3572A5", "Vue": "#41b883", "Kotlin": "#A97BFF", "Dart": "#00B4AB",
    "Shell": "#89e051", "Go": "#00ADD8", "C++": "#f34b7d", "C": "#555555",
}
DEFAULT_COLOR = "#7c3aed"

FALLBACK = {
    "repos": 11,
    "years": datetime.date.today().year - 2018,
    "langs": [("TypeScript", 40), ("JavaScript", 20), ("Java", 20),
              ("SCSS", 10), ("C#", 10)],
}


def _api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "User-Agent": f"{USER}-readme",
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {os.environ['GH_TOKEN']}"}
               if os.environ.get("GH_TOKEN") else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    try:
        user = _api(f"/users/{USER}")
        years = datetime.date.today().year - int(user["created_at"][:4])
        repos_meta = _api(f"/users/{USER}/repos?per_page=100&type=owner")
        bytes_by_lang = {}
        for repo in repos_meta:
            if repo.get("fork"):
                continue
            try:
                for lang, n in _api(f"/repos/{USER}/{repo['name']}/languages").items():
                    bytes_by_lang[lang] = bytes_by_lang.get(lang, 0) + n
            except urllib.error.URLError:
                continue
        top = sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)[:5]
        total = sum(n for _, n in top) or 1
        langs = [(name, round(n * 100 / total)) for name, n in top]
        return {"repos": user["public_repos"], "years": years, "langs": langs}
    except Exception as e:  # network blocked / rate-limited / parse error
        print("fetch failed, using fallback:", e)
        return FALLBACK


def render(s):
    bx, bw = 612, 516
    segs, x = [], bx
    for i, (name, pct) in enumerate(s["langs"]):
        w = bw * pct / 100 if i < len(s["langs"]) - 1 else bx + bw - x
        color = LANG_COLORS.get(name, DEFAULT_COLOR)
        segs.append(f'<rect x="{x:.0f}" y="116" width="{w:.0f}" height="22" fill="{color}"/>')
        x += w
    # legend: up to 3 on first row, rest on second
    pos = [(612, 168), (792, 168), (972, 168), (612, 200), (792, 200)]
    legend = []
    for (name, pct), (lx, ly) in zip(s["langs"], pos):
        color = LANG_COLORS.get(name, DEFAULT_COLOR)
        legend.append(
            f'<g transform="translate({lx},{ly})"><circle cx="7" cy="-4" r="6" fill="{color}"/>'
            f'<text x="22" y="0">{name} <tspan fill="#6b6680" font-weight="500">{pct}%</tspan></text></g>')
    yr = s["years"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" fill="none" role="img" aria-label="GitHub overview">
  <defs>
    <linearGradient id="num" gradientUnits="userSpaceOnUse" x1="70" y1="120" x2="360" y2="240"><stop offset="0%" stop-color="#7c3aed"/><stop offset="55%" stop-color="#2563eb"/><stop offset="100%" stop-color="#c026d3"/></linearGradient>
    <linearGradient id="card" x1="0" y1="0" x2="0.5" y2="1"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.80"/><stop offset="100%" stop-color="#f1ecff" stop-opacity="0.64"/></linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="50%" stop-color="#fff" stop-opacity="0.9"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <radialGradient id="ov" cx="0.5" cy="0.5" r="0.5"><stop offset="0%" stop-color="#a855f7" stop-opacity="0.3"/><stop offset="100%" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
    <radialGradient id="ob" cx="0.5" cy="0.5" r="0.5"><stop offset="0%" stop-color="#38bdf8" stop-opacity="0.28"/><stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/></radialGradient>
    <filter id="cs" x="-15%" y="-15%" width="130%" height="150%"><feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#5b3fae" flood-opacity="0.18"/></filter>
    <filter id="bz" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="34"/></filter>
    <clipPath id="cc"><rect x="24" y="18" width="1152" height="264" rx="28"/></clipPath>
    <clipPath id="bar"><rect x="612" y="116" width="516" height="22" rx="11"/></clipPath>
  </defs>

  <g filter="url(#cs)"><rect x="24" y="18" width="1152" height="264" rx="28" fill="url(#card)" stroke="#fff" stroke-opacity="0.9" stroke-width="1.5"/></g>
  <g clip-path="url(#cc)"><circle cx="120" cy="60" r="160" fill="url(#ov)" filter="url(#bz)"/><circle cx="1080" cy="250" r="160" fill="url(#ob)" filter="url(#bz)"/></g>
  <rect x="64" y="19" width="1072" height="1.5" fill="url(#sheen)"/>

  <g font-family="{FONT}">
    <text x="60" y="64" fill="#7c3aed" font-size="13" font-weight="800" letter-spacing="4">OVERVIEW</text>

    <g transform="translate(56,82)"><rect width="232" height="84" rx="18" fill="#ffffff" fill-opacity="0.55" stroke="#7c3aed" stroke-opacity="0.14"/>
      <text x="20" y="50" font-size="38" font-weight="800" fill="url(#num)">{s["repos"]}</text>
      <text x="98" y="38" font-size="14" font-weight="700" fill="#3a3550">Public</text>
      <text x="98" y="58" font-size="14" font-weight="700" fill="#3a3550">Repositories</text>
    </g>
    <g transform="translate(300,82)"><rect width="232" height="84" rx="18" fill="#ffffff" fill-opacity="0.55" stroke="#7c3aed" stroke-opacity="0.14"/>
      <text x="20" y="50" font-size="38" font-weight="800" fill="url(#num)">{yr}<tspan font-size="20">yr</tspan></text>
      <text x="100" y="38" font-size="14" font-weight="700" fill="#3a3550">on GitHub</text>
      <text x="100" y="58" font-size="13" font-weight="600" fill="#6b6680">since 2018</text>
    </g>
    <g transform="translate(56,178)"><rect width="232" height="84" rx="18" fill="#ffffff" fill-opacity="0.55" stroke="#7c3aed" stroke-opacity="0.14"/>
      <text x="20" y="50" font-size="38" font-weight="800" fill="url(#num)">{FEATURED}</text>
      <text x="76" y="38" font-size="14" font-weight="700" fill="#3a3550">Featured</text>
      <text x="76" y="58" font-size="14" font-weight="700" fill="#3a3550">Projects</text>
    </g>
    <g transform="translate(300,178)"><rect width="232" height="84" rx="18" fill="#ffffff" fill-opacity="0.55" stroke="#7c3aed" stroke-opacity="0.14"/>
      <text x="20" y="50" font-size="38" font-weight="800" fill="url(#num)">1</text>
      <circle cx="64" cy="33" r="4" fill="#059669"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" repeatCount="indefinite"/></circle>
      <text x="76" y="38" font-size="14" font-weight="700" fill="#3a3550">Live Service</text>
      <text x="76" y="58" font-size="13" font-weight="600" fill="#047857">{LIVE}</text>
    </g>

    <line x1="572" y1="64" x2="572" y2="248" stroke="#7c3aed" stroke-opacity="0.12" stroke-width="1.5"/>

    <text x="612" y="64" fill="#7c3aed" font-size="13" font-weight="800" letter-spacing="4">MOST USED LANGUAGES</text>
    <text x="612" y="98" fill="#6b6680" font-size="13" font-weight="500">저장소 바이트 기준 · Frontend 중심</text>

    <g clip-path="url(#bar)">{''.join(segs)}</g>
    <rect x="612" y="116" width="516" height="22" rx="11" fill="none" stroke="#ffffff" stroke-opacity="0.6"/>

    <g font-size="14" font-weight="600" fill="#3a3550">{''.join(legend)}</g>

    <g transform="translate(612,228)" font-size="12.5" font-weight="600" fill="#463f5e">
      <g><rect width="92" height="28" rx="14" fill="#7c3aed" fill-opacity="0.1" stroke="#7c3aed" stroke-opacity="0.3"/><text x="46" y="19" text-anchor="middle" fill="#6d28d9">React</text></g>
      <g transform="translate(100,0)"><rect width="118" height="28" rx="14" fill="#7c3aed" fill-opacity="0.1" stroke="#7c3aed" stroke-opacity="0.3"/><text x="59" y="19" text-anchor="middle" fill="#6d28d9">TypeScript</text></g>
      <g transform="translate(226,0)"><rect width="138" height="28" rx="14" fill="#7c3aed" fill-opacity="0.1" stroke="#7c3aed" stroke-opacity="0.3"/><text x="69" y="19" text-anchor="middle" fill="#6d28d9">Interactive Web</text></g>
    </g>
  </g>
</svg>
'''


if __name__ == "__main__":
    stats = fetch_stats()
    print("stats:", stats)
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "github.svg")
    with open(out, "w") as f:
        f.write(render(stats))
    print("wrote", os.path.normpath(out))
