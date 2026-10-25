"""Generate dark/light SVG cards and README.md from data/profile.json (+ data/stats.json)."""
import json, textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "data/profile.json").read_text())
sp = ROOT / "data/stats.json"
S = json.loads(sp.read_text()) if sp.exists() else {}
W = 800
ACCENT = "#4493f8"
THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", line="#30363d", text="#f0f6fc", mute="#8b949e", chip="#21262d", accent=ACCENT, green="#3fb950"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", line="#d0d7de", text="#1f2328", mute="#59636e", chip="#eaeef2", accent="#0969da", green="#1a7f37"),
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"


def svg(w, h, body, t, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>'
            f'<style>.s{{font-family:{SANS}}}.m{{font-family:{MONO}}}</style>{body}</svg>')


def panel(w, h, t):
    return f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>'


def text(x, y, s, cls, size, fill, weight=400, ls=0):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" font-weight="{weight}" letter-spacing="{ls}">{escape(s)}</text>'


def chips(x, y, items, t, maxw):
    out, cx, cy = [], x, y
    for c in items:
        w = len(c) * 7 + 20
        if cx + w > x + maxw:
            cx, cy = x, cy + 30
        out.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="22" rx="11" fill="{t["chip"]}" stroke="{t["line"]}"/>')
        out.append(text(cx + 10, cy + 15, c, "m", 11, t["mute"]))
        cx += w + 8
    return "".join(out), cy + 22


def hero(t):
    h = 230
    b = panel(W, h, t) + f'<rect x="32" y="36" width="8" height="8" fill="{t["accent"]}"/>' + text(48, 44, "BACKEND · FULL-STACK", "m", 11, t["mute"], ls=3)
    b += text(32, 96, P["name"], "s", 44, t["text"], 800, -1)
    b += text(32, 126, f'{P["headline"]} · {P["sub"]}', "s", 16, t["mute"])
    for i, line in enumerate(textwrap.wrap(P["bio"], 88)):
        b += text(32, 160 + i * 20, line, "s", 14, t["text"])
    b += f'<circle cx="38" cy="205" r="5" fill="{t["green"]}"/>' + text(52, 209, P["status"], "m", 12, t["green"])
    return svg(W, h, b, t, f'{P["name"]}: {P["headline"]}, {P["sub"]}. {P["bio"]} {P["status"]}.'), h


def button(link, t):
    w = len(link["label"]) * 8 + 40
    b = f'<rect x="0.5" y="0.5" width="{w-1}" height="39" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>' + text(w / 2 - len(link["label"]) * 3.7, 25, link["label"], "s", 13, t["text"], 600)
    return svg(w, 40, b, t, link["label"]), w


def stats(t):
    h, n = 120, len(P["stats"])
    cw = W / n
    b = panel(W, h, t)
    for i, s in enumerate(P["stats"]):
        x = i * cw + 24
        if i:
            b += f'<line x1="{i*cw}" y1="24" x2="{i*cw}" y2="{h-24}" stroke="{t["line"]}"/>'
        b += text(x, 62, s["value"], "s", 34, t["text"], 800, -1) + text(x, 84, s["label"], "m", 9, t["mute"], ls=1.5) + text(x, 100, s["note"], "m", 10, t["accent"])
    summary = "; ".join(f'{s["value"]} {s["label"].lower()} ({s["note"]})' for s in P["stats"])
    return svg(W, h, b, t, "Impact: " + summary), h


def project(p, t):
    d, hl = textwrap.wrap(p["desc"], 92), textwrap.wrap(p["highlight"], 92)
    y = 84 + len(d) * 20
    b0 = text(24, 34, p["name"], "s", 22, t["text"], 700) + text(24 + len(p["name"]) * 13 + 14, 34, p["tag"], "m", 10, t["accent"], ls=2)
    b0 += f'<text x="{W-24}" y="34" text-anchor="end" class="m" font-size="12" fill="{t["mute"]}">↗ GitHub</text>'
    for i, l in enumerate(d):
        b0 += text(24, 62 + i * 20, l, "s", 14, t["text"])
    for i, l in enumerate(hl):
        b0 += text(24, y + i * 20, ("▸ " if i == 0 else "   ") + l, "s", 13, t["mute"])
    cy = y + len(hl) * 20 + 8
    cb, end = chips(24, cy, p["chips"], t, W - 48)
    h = end + 22
    return svg(W, h, panel(W, h, t) + b0 + cb, t, f'{p["name"]} ({p["tag"].title()}): {p["desc"]} {p["highlight"]}'), h


def label(s, t):
    b = f'<rect x="0" y="12" width="8" height="8" fill="{t["accent"]}"/>' + text(16, 20, s, "m", 12, t["mute"], ls=3)
    return svg(W, 32, b, t, s.title())


def stack(t):
    h = 36 + len(P["stack"]) * 36
    b = panel(W, h, t)
    for i, (k, v) in enumerate(P["stack"]):
        y = 38 + i * 36
        b += text(24, y, k, "m", 11, t["accent"], ls=2) + text(140, y, v, "s", 14, t["text"])
    return svg(W, h, b, t, "Stack. " + ". ".join(f"{k.title()}: {v}" for k, v in P["stack"])), h


def experience(t):
    h = 36 + len(P["experience"]) * 44
    b = panel(W, h, t)
    for i, e in enumerate(P["experience"]):
        y = 40 + i * 44
        b += f'<circle cx="30" cy="{y-5}" r="5" fill="{t["accent"]}"/>'
        if i < len(P["experience"]) - 1:
            b += f'<line x1="30" y1="{y+2}" x2="30" y2="{y+34}" stroke="{t["line"]}"/>'
        b += text(48, y, e["role"], "s", 15, t["text"], 600) + text(48 + len(e["role"]) * 8.4 + 12, y, "@ " + e["where"], "s", 15, t["mute"])
        b += f'<text x="{W-24}" y="{y}" text-anchor="end" class="m" font-size="12" fill="{t["mute"]}">{escape(e["when"])}</text>'
    return svg(W, h, b, t, "Experience: " + "; ".join(f'{e["role"]} at {e["where"]}, {e["when"]}' for e in P["experience"])), h


def telemetry(t):
    h = 150
    contrib = f'{S["contributions"]:,}' if "contributions" in S else "—"
    repos = str(S.get("repos", "—"))
    langs = S.get("languages", [])
    b = panel(W, h, t) + f'<rect x="24" y="26" width="8" height="8" fill="{t["accent"]}"/>' + text(40, 34, "GITHUB ACTIVITY", "m", 11, t["mute"], ls=3)
    b += text(24, 98, contrib, "s", 48, t["text"], 800, -1) + text(24, 122, "CONTRIBUTIONS · PAST YEAR", "m", 9, t["mute"], ls=1.5)
    b += f'<line x1="270" y1="26" x2="270" y2="{h-26}" stroke="{t["line"]}"/>'
    b += text(294, 98, repos, "s", 48, t["text"], 800, -1) + text(294, 122, "PUBLIC REPOSITORIES", "m", 9, t["mute"], ls=1.5)
    b += f'<line x1="500" y1="26" x2="500" y2="{h-26}" stroke="{t["line"]}"/>' + text(524, 50, "LANGUAGES", "m", 10, t["mute"], ls=3)
    for i, (l, n) in enumerate(langs[:5]):
        y = 72 + i * 16
        b += text(524, y, l, "m", 11, t["text"]) + f'<rect x="640" y="{y-8}" width="{max(6, 130*n/langs[0][1])}" height="6" rx="3" fill="{t["accent"]}" opacity="{1-i*0.15}"/>'
    return svg(W, h, b, t, f"GitHub activity: {contrib} contributions in the past year, {repos} public repositories. Top languages: {', '.join(l for l, _ in langs)}."), h


def main():
    raw = f'https://raw.githubusercontent.com/{P["user"]}/{P["repo"]}/main/assets'
    parts = {}

    def emit(name, fn):
        alt = None
        for th, t in THEMES.items():
            s, extra = fn(t)
            (ROOT / f"assets/{th}/{name}.svg").write_text(s)
            alt = s.split('aria-label="')[1].split('"')[0]
        return alt, extra

    def pic(name, alt, attrs='width="100%"'):
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{raw}/dark/{name}.svg">'
                f'<source media="(prefers-color-scheme: light)" srcset="{raw}/light/{name}.svg">'
                f'<img src="{raw}/light/{name}.svg" {attrs} alt="{alt}"></picture>')

    out = ['<!-- Generated by scripts/build.py from data/profile.json. Edit that file instead; changes here are overwritten. -->', '<div align="center">', '']
    a, _ = emit("hero", hero); out += [pic("hero", a), '']
    btns = []
    for l in P["links"]:
        a, _ = emit(f"button-{l['id']}", lambda t, l=l: button(l, t))
        btns.append(f'<a href="{l["url"]}">{pic("button-" + l["id"], a, "height=\"40\"")}</a>')
    out += ["&nbsp;".join(btns), '']
    a, _ = emit("stats", stats); out += [pic("stats", a), '']
    a, _ = emit("label-work", lambda t: (label("SELECTED WORK", t), 0)); out += [pic("label-work", "Selected work")]
    for p in P["projects"]:
        a, _ = emit(f"project-{p['id']}", lambda t, p=p: project(p, t))
        out.append(f'<a href="{p["url"]}">{pic("project-" + p["id"], a)}</a>')
    out.append('')
    for key, lab, fn in [("stack", "STACK", stack), ("experience", "EXPERIENCE", experience)]:
        emit(f"label-{key}", lambda t, lab=lab: (label(lab, t), 0)); out.append(pic(f"label-{key}", lab.title()))
        a, _ = emit(key, fn); out += [pic(key, a), '']
    emit("label-activity", lambda t: (label("ACTIVITY", t), 0)); out.append(pic("label-activity", "Activity"))
    a, _ = emit("telemetry", telemetry); out += [pic("telemetry", a), '']
    out += [f'<sub>{escape(P["footer"])} <a href="{P["links"][-1]["url"]}">Say hi</a>.</sub>', '', '</div>', '']
    (ROOT / "README.md").write_text("\n".join(out))


main()
