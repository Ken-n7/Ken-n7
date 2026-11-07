"""Builds assets/terminal.svg: a GNOME Terminal window (Ubuntu, Yaru dark) that
types out the session below.

Edit SESSION, then run:  python3 assets/terminal.py
Needs fonttools + brotli (pip install fonttools brotli) and the Ubuntu fonts
(/usr/share/fonts/truetype/ubuntu, preinstalled on Ubuntu).
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Each step is a command and its output. Output lines are lists of (text, style).
SESSION = [
    ("whoami", [[("ken", "")]]),
    ("cat about.txt", [
        [("John Kenneth Cañete, developer.", "")],
        [("", "")],
        [("I build stuff: web apps, multiplayer games, desktop tools,", "")],
        [("and the occasional experiment. I like taking an idea all the", "")],
        [("way to something people can actually click, play and use.", "")],
    ]),
    ("ls ~/builds", [
        [("lakbayin", "dir"), ("        ", ""), ("probxcape", "dir"), ("       ", ""), ("integrid", "dir"), ("        ", ""), ("swarm-gallery", "dir")],
        [("efp-supply", "dir"), ("      ", ""), ("relivetv", "dir"), ("        ", ""), ("sip-and-savor", "dir"), ("   ", ""), ("tagtune", "dir")],
    ]),
    ("cat status", [[("●", "ok"), (" open to work. email is the easiest way to reach me.", "")]]),
]

FONT = 1000 * 11 / 560  # px: Ubuntu Sans Mono is 560/1000 em wide, so each character is exactly 11px
ADV = 11.0
LINE = 30          # line height
PAD_X, BAR = 22, 47  # terminal padding, header bar height
M = 28             # margin around the window for its shadow
W = 960            # window width
TYPE = 0.06        # seconds per typed character
# GNOME Terminal's default palette (bg, fg, and the colors Ubuntu's prompt and ls use)
COLORS = dict(bg="#171421", fg="#D0CFCC", bar="#2C2C2C", title="#FFFFFF", icon="#E6E6E6",
              user="#26A269", path="#2A7BDE", dir="#2A7BDE", ok="#33D17A")
PROMPT = [("ken@github", "user"), (":", ""), ("~", "path"), ("$ ", "")]
TITLE = "ken@github: ~"

ROOT = Path(__file__).resolve().parent
UBUNTU = "/usr/share/fonts/truetype/ubuntu/"


def font_b64(file: str, axes: dict, chars: str) -> str:
    """One static weight of a variable Ubuntu font, cut down to `chars`, as base64 woff2."""
    font = instancer.instantiateVariableFont(TTFont(UBUNTU + file), axes)
    opts = subset.Options()
    opts.flavor = "woff2"
    s = subset.Subsetter(opts)
    s.populate(text=chars)
    s.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def spans(parts):
    out = []
    for text, cls in parts:
        style = f' class="{cls}"' if cls else ""
        out.append(f"<tspan{style}>{esc(text)}</tspan>")
    return "".join(out)


def main():
    rows, css, t, y = [], [], 0.5, M + BAR + 34
    plen = sum(len(p[0]) for p in PROMPT)
    for i, (cmd, output) in enumerate(SESSION):
        # prompt line, then the command typed behind a sliding cover
        css.append(f".p{i}{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
        x0 = M + PAD_X + plen * ADV
        start = t + 0.35
        dur = len(cmd) * TYPE
        w = len(cmd) * ADV
        rows.append(f'<g class="p{i}"><text x="{M + PAD_X}" y="{y}">{spans(PROMPT)}<tspan>{esc(cmd)}</tspan></text>'
                    f'<rect class="cv{i}" x="{x0:.1f}" y="{y - FONT:.1f}" width="{w + ADV + 2:.1f}" height="{LINE}" fill="{COLORS["bg"]}"/>'
                    f'<rect class="cu{i}" x="{x0:.1f}" y="{y - FONT + 2:.1f}" width="{ADV:.1f}" height="{FONT + 3:.1f}" fill="{COLORS["fg"]}"/></g>')
        # n+1 steps to one character past the end: the last step shown while
        # running already reveals the whole command, whatever the end state.
        n = len(cmd) + 1
        css.append(f".cv{i}{{animation:type{i} {dur + TYPE:.2f}s steps({n}) {start:.2f}s forwards,off 0s {start + dur + 0.25:.2f}s forwards}}")
        css.append(f".cu{i}{{animation:type{i} {dur + TYPE:.2f}s steps({n}) {start:.2f}s forwards,off 0s {start + dur + 0.25:.2f}s forwards}}")
        css.append(f"@keyframes type{i}{{to{{transform:translateX({w + ADV + 2:.1f}px)}}}}")
        t = start + dur + 0.3
        y += LINE
        # output appears all at once, like a real terminal
        css.append(f".o{i}{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
        rows.append(f'<g class="o{i}">' + "".join(
            f'<text x="{M + PAD_X}" y="{y + k * LINE}">{spans(line)}</text>' for k, line in enumerate(output)) + "</g>")
        y += LINE * len(output) + 10
        t += 0.45
    # final prompt with a blinking cursor
    css.append(f".pf{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
    xf = M + PAD_X + plen * ADV
    rows.append(f'<g class="pf"><text x="{M + PAD_X}" y="{y}">{spans(PROMPT)}</text>'
                f'<rect class="blink" x="{xf:.1f}" y="{y - FONT + 2:.1f}" width="{ADV:.1f}" height="{FONT + 3:.1f}" fill="{COLORS["fg"]}"/></g>')
    H = y + 26 + M  # canvas height; the window spans M..H-M

    used = "".join(c for _, out in SESSION for line in out for text, _ in line for c in text)
    used += "".join(cmd for cmd, _ in SESSION) + "".join(p[0] for p in PROMPT)
    regular = font_b64("UbuntuSansMono[wght].ttf", {"wght": 400}, used)
    bold = font_b64("UbuntuSansMono[wght].ttf", {"wght": 700}, used)
    title = font_b64("UbuntuSans[wdth,wght].ttf", {"wght": 700, "wdth": 100}, TITLE)

    c = COLORS
    X0, X1, Y0, Y1 = M, M + W, M, H - M  # window edges
    by = Y0 + BAR / 2                     # header bar centre line
    # header bar buttons, drawn like GNOME's symbolic icons
    btn = lambda cx, inner: (f'<circle cx="{cx}" cy="{by}" r="12" fill="#FFFFFF" fill-opacity=".1"/>'
                             f'<g transform="translate({cx} {by})" stroke="{c["icon"]}" stroke-width="1.6" fill="none" stroke-linecap="round">{inner}</g>')
    flat = lambda cx, inner: (f'<g transform="translate({cx} {by})" stroke="{c["icon"]}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')
    chrome = "".join([
        flat(X0 + 26, '<path d="M-6 0h12M0-6v12"/>'),                                  # new tab
        flat(X1 - 154, '<circle cx="-1.5" cy="-1.5" r="5"/><path d="M2.3 2.3 6.5 6.5"/>'),  # search
        flat(X1 - 120, '<path d="M-6-4.5h12M-6 0h12M-6 4.5h12"/>'),                    # menu
        btn(X1 - 84, '<path d="M-4.5 3h9"/>'),                                          # minimize
        btn(X1 - 52, '<rect x="-4" y="-4" width="8" height="8" rx="1"/>'),              # maximize
        btn(X1 - 20, '<path d="M-4-4 4 4M4-4-4 4"/>'),                                  # close
    ])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * M} {H}" width="{W + 2 * M}" height="{H}" role="img" aria-label="GNOME Terminal: whoami, ken. John Kenneth Cañete, developer. I build stuff: web apps, multiplayer games, desktop tools, and the occasional experiment. Builds: lakbayin, probxcape, integrid, swarm-gallery, efp-supply, relivetv, sip-and-savor, tagtune. Status: open to work.">
<style>
@font-face{{font-family:M;src:url(data:font/woff2;base64,{regular}) format('woff2');font-weight:400}}
@font-face{{font-family:M;src:url(data:font/woff2;base64,{bold}) format('woff2');font-weight:700}}
@font-face{{font-family:T;src:url(data:font/woff2;base64,{title}) format('woff2');font-weight:700}}
text{{font-family:M,'Ubuntu Sans Mono',ui-monospace,monospace;font-size:{FONT:.4f}px;fill:{c["fg"]};white-space:pre}}
.user{{fill:{c["user"]};font-weight:700}} .path{{fill:{c["path"]};font-weight:700}}
.dir{{fill:{c["dir"]};font-weight:700}} .ok{{fill:{c["ok"]}}}
.title{{font-family:T,'Ubuntu Sans',Cantarell,sans-serif;font-weight:700;font-size:15px;fill:{c["title"]}}}
.blink{{animation:blink 1.06s steps(1) infinite}}
@keyframes on{{to{{opacity:1}}}} @keyframes off{{to{{opacity:0}}}} @keyframes blink{{50%{{opacity:0}}}}
{chr(10).join(css)}
@media (prefers-reduced-motion:reduce){{[class^="p"],[class^="o"]{{opacity:1!important;animation:none!important}} [class^="cv"],[class^="cu"]{{display:none}}}}
</style>
<defs>
<filter id="sh" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#000" flood-opacity=".38"/></filter>
<clipPath id="win"><rect x="{X0}" y="{Y0}" width="{W}" height="{Y1 - Y0}" rx="12"/></clipPath>
</defs>
<rect x="{X0}" y="{Y0}" width="{W}" height="{Y1 - Y0}" rx="12" fill="#000" filter="url(#sh)"/>
<rect x="{X0}" y="{Y0}" width="{W}" height="{Y1 - Y0}" rx="12" fill="{c["bg"]}"/>
<g clip-path="url(#win)">
<rect x="{X0}" y="{Y0}" width="{W}" height="{BAR}" fill="{c["bar"]}"/>
<rect x="{X0}" y="{Y0 + BAR - 1}" width="{W}" height="1" fill="#000" fill-opacity=".45"/>
{chrome}
<text class="title" x="{X0 + W / 2}" y="{by + 5}" text-anchor="middle">{TITLE}</text>
{chr(10).join(rows)}
</g>
<rect x="{X0 + .5}" y="{Y0 + .5}" width="{W - 1}" height="{Y1 - Y0 - 1}" rx="11.5" fill="none" stroke="#FFFFFF" stroke-opacity=".1"/>
</svg>'''
    (ROOT / "terminal.svg").write_text(svg)
    print(f"terminal.svg: {W + 2 * M}x{H}, {len(svg) // 1024} KB, plays for {t:.1f}s")


if __name__ == "__main__":
    main()
