# Generates animated preview HTML replicating the Codex app's rendering.
# Durations match app source: m(row,n,base,last); idle is played 6x slow.

states = [
    ("idle",          0, 6, [280,110,110,140,140,320], 6.0),
    ("running-right", 1, 8, [120]*7+[220], None),
    ("running-left",  2, 8, [120]*7+[220], None),
    ("waving",        3, 4, [140]*3+[280], None),
    ("jumping",       4, 5, [140]*4+[280], None),
    ("failed",        5, 8, [140]*7+[240], None),
    ("waiting",       6, 6, [150]*5+[260], None),
    ("running",       7, 6, [120]*5+[220], None),
    ("review",        8, 6, [150]*5+[280], None),
]

def dur_mult(d, m):
    return [round(x*m) for x in d]

frames = []
for name, row, n, d, mult in states:
    if mult:
        d = dur_mult(d, mult)
    total = sum(d)
    keyframes = []
    acc = 0
    for i in range(n):
        pct = acc / total * 100
        x = i / (8 - 1) * 100
        y = row / (9 - 1) * 100
        keyframes.append(f"{pct:.3f}%{{background-position:{x:.2f}% {y:.2f}%}}")
        acc += d[i]
    keyframes.append(f"100%{{background-position:{(n-1)/(8-1)*100:.2f}% {row/(9-1)*100:.2f}%}}")
    total_sec = total / 1000
    frames.append(dict(name=name, row=row, n=n, d=d, total=total,
                       total_sec=total_sec, kf=keyframes))

html = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Bitty preview</title>
<style>
body{background:#0b1020;color:#dfe7ff;font-family:'Segoe UI',system-ui,sans-serif;margin:0;padding:24px;}
h1{font-size:18px;margin:0 0 4px;color:#7ee0f5;letter-spacing:1px}
.sub{font-size:12px;color:#6b7a9e;margin-bottom:20px}
.pet{width:192px;height:208px;background-image:url('spritesheet.png');background-size:800% 900%;image-rendering:pixelated;transform-origin:top left}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.card{background:#141c33;border:1px solid #243052;border-radius:10px;padding:10px}
.card .lbl{font-size:12px;color:#9db4e8;margin-bottom:8px}
.card .lbl b{color:#ffd76e}
.meta{font-size:11px;color:#5c6b8f;margin-top:6px}
"""
for i, f in enumerate(frames):
    html += f"@keyframes k{i}{{{' '.join(f['kf'])}}}\n"
html += "</style></head><body>"
html += "<h1>月绒 MOONWOOL · 奶油绒团小兽</h1>"
html += "<div class='sub'>与 App 相同的帧时长渲染（idle 按 6 倍慢放）。9 种状态按顺序播放。</div><div class='grid'>"
for i, f in enumerate(frames):
    html += f"<div class='card'><div class='lbl'>{i}: <b>{f['name']}</b></div>"
    html += f"<div class='pet' style='animation:k{i} {f['total_sec']:.2f}s steps(1,end) infinite'></div>"
    html += f"<div class='meta'>{f['n']} 帧 · 周期 {f['total_sec']:.2f}s</div></div>"
html += "</div></body></html>"
open("preview.html", "w", encoding="utf-8").write(html)
print("wrote preview.html")
