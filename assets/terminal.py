"""Builds assets/terminal.svg: a terminal window that types out the session below.

Edit SESSION, then run:  python3 assets/terminal.py
Needs fonttools + brotli (pip install fonttools brotli) and DejaVu Sans Mono.
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

# Each step is a command and its output. Output lines are lists of (text, style).
SESSION = [
    ("whoami", [[("ken", "")]]),
    ("cat about.txt", [
        [("John Kenneth Cañete, developer from the Philippines.", "")],
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

FONT = 2048 * 11 / 1233  # px: makes each character exactly 11px wide, so no browser rounds it
ADV = 11.0         # DejaVu Sans Mono advance (1233/2048 em)
LINE = 28          # line height
PAD_X, TOP = 28, 76
W = 960
TYPE = 0.06        # seconds per typed character
COLORS = dict(bg="#121413", bar="#232723", fg="#ECEEEB", muted="#A5ABA5",
              user="#B2C9A5", path="#82AAFF", dir="#82AAFF", ok="#B2C9A5")
PROMPT = [("ken@github", "user"), (":", ""), ("~", "path"), ("$ ", "")]

ROOT = Path(__file__).resolve().parent
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono{}.ttf"


def font_b64(style: str, chars: str) -> str:
    font = TTFont(DEJAVU.format(style))
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
    rows, css, t, y = [], [], 0.5, TOP
    plen = sum(len(p[0]) for p in PROMPT)
    for i, (cmd, output) in enumerate(SESSION):
        # prompt line, then the command typed behind a sliding cover
        css.append(f".p{i}{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
        x0 = PAD_X + plen * ADV
        start = t + 0.35
        dur = len(cmd) * TYPE
        w = len(cmd) * ADV
        rows.append(f'<g class="p{i}"><text x="{PAD_X}" y="{y}">{spans(PROMPT)}<tspan>{esc(cmd)}</tspan></text>'
                    f'<rect class="cv{i}" x="{x0:.1f}" y="{y - FONT:.1f}" width="{w + ADV + 2:.1f}" height="{LINE}" fill="{COLORS["bg"]}"/>'
                    f'<rect class="cu{i}" x="{x0:.1f}" y="{y - FONT + 2:.1f}" width="{ADV:.1f}" height="{FONT + 3:.1f}" fill="{COLORS["fg"]}"/></g>')
        # n+1 steps to one character past the end: the last step shown while
        # running already reveals the whole command, whatever the end state.
        n = len(cmd) + 1
        css.append(f".cv{i}{{animation:type{i} {dur + TYPE:.2f}s steps({n}) {start:.2f}s forwards}}")
        css.append(f".cu{i}{{animation:type{i} {dur + TYPE:.2f}s steps({n}) {start:.2f}s forwards,off 0s {start + dur + 0.25:.2f}s forwards}}")
        css.append(f"@keyframes type{i}{{to{{transform:translateX({w + ADV + 2:.1f}px)}}}}")
        t = start + dur + 0.3
        y += LINE
        # output appears all at once, like a real terminal
        css.append(f".o{i}{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
        rows.append(f'<g class="o{i}">' + "".join(
            f'<text x="{PAD_X}" y="{y + k * LINE}">{spans(line)}</text>' for k, line in enumerate(output)) + "</g>")
        y += LINE * len(output) + 10
        t += 0.45
    # final prompt with a blinking cursor
    css.append(f".pf{{opacity:0;animation:on 0s {t:.2f}s forwards}}")
    xf = PAD_X + plen * ADV
    rows.append(f'<g class="pf"><text x="{PAD_X}" y="{y}">{spans(PROMPT)}</text>'
                f'<rect class="blink" x="{xf:.1f}" y="{y - FONT + 2:.1f}" width="{ADV:.1f}" height="{FONT + 3:.1f}" fill="{COLORS["fg"]}"/></g>')
    H = y + 30

    used = "".join(c for _, out in SESSION for line in out for text, _ in line for c in text)
    used += "".join(cmd for cmd, _ in SESSION) + "".join(p[0] for p in PROMPT) + "ken@github: ~"
    regular = font_b64("", used)
    bold = font_b64("-Bold", used)

    c = COLORS
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: whoami, ken. John Kenneth Cañete, developer from the Philippines. I build stuff: web apps, multiplayer games, desktop tools, and the occasional experiment. Builds: lakbayin, probxcape, integrid, swarm-gallery, efp-supply, relivetv, sip-and-savor, tagtune. Status: open to work.">
<style>
@font-face{{font-family:M;src:url(data:font/woff2;base64,{regular}) format('woff2');font-weight:400}}
@font-face{{font-family:M;src:url(data:font/woff2;base64,{bold}) format('woff2');font-weight:700}}
text{{font-family:M,ui-monospace,monospace;font-size:{FONT:.4f}px;fill:{c["fg"]};white-space:pre}}
.user{{fill:{c["user"]};font-weight:700}} .path{{fill:{c["path"]};font-weight:700}}
.dir{{fill:{c["dir"]};font-weight:700}} .ok{{fill:{c["ok"]}}}
.title{{fill:{c["muted"]};font-size:14px}}
.blink{{animation:blink 1.06s steps(1) infinite}}
@keyframes on{{to{{opacity:1}}}} @keyframes off{{to{{opacity:0}}}} @keyframes blink{{50%{{opacity:0}}}}
{chr(10).join(css)}
@media (prefers-reduced-motion:reduce){{[class^="p"],[class^="o"]{{opacity:1!important;animation:none!important}} [class^="cv"],[class^="cu"]{{display:none}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}" stroke="#ECEEEB" stroke-opacity=".12"/>
<path d="M.5 12.5a12 12 0 0 1 12-12h{W - 25}a12 12 0 0 1 12 12V40H.5z" fill="{c["bar"]}"/>
<circle cx="24" cy="20" r="6.5" fill="#FF5F57"/><circle cx="46" cy="20" r="6.5" fill="#FEBC2E"/><circle cx="68" cy="20" r="6.5" fill="#28C840"/>
<text class="title" x="{W / 2}" y="25" text-anchor="middle">ken@github: ~</text>
{chr(10).join(rows)}
</svg>'''
    (ROOT / "terminal.svg").write_text(svg)
    print(f"terminal.svg: {W}x{H}, {len(svg) // 1024} KB, plays for {t:.1f}s")


if __name__ == "__main__":
    main()
