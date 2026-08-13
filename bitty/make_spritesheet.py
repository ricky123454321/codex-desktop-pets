# 8-bit pixel block robot pet spritesheet generator
# Grid: 8 cols x 9 rows, cells 192x208, spritesheet 1536x1872
# Logical grid per cell: 24 x 26, pixel scale PX=8

from PIL import Image

# ---- palette (RGBA) ----
OUT    = (16, 24, 40, 255)        # outline / darkest
BODY_D = (24, 40, 80, 255)        # body shadow navy
BODY_M = (40, 66, 122, 255)       # body mid blue
BODY_L = (74, 106, 176, 255)      # body highlight
SCR_BG = (14, 84, 106, 255)       # dim cyan screen bg
SCR_ON = (52, 211, 235, 255)      # lit cyan
EYE    = (5, 34, 42, 255)         # dark pixels on screen
ANT    = (250, 204, 21, 255)      # gold antenna glow
ANT_DM = (120, 98, 20, 255)       # dim gold
SHAD   = (12, 20, 34, 70)         # translucent shadow
DUST   = (90, 120, 170, 255)      # impact dust

W, H = 24, 26
PX = 8
CELL_W, CELL_H = 192, 208
NCOLS, NROWS = 8, 9

BASE_BX, BASE_BY = 4, 8           # body top-left in rest pose

# ---- canvas helpers ----
def new_cell():
    return [[None] * W for _ in range(H)]

def put(g, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c

def rect(g, x, y, w, h, c):
    for yy in range(max(0, y), min(H, y + h)):
        for xx in range(max(0, x), min(W, x + w)):
            g[yy][xx] = c

def hline(g, x, y, w, c):
    for xx in range(max(0, x), min(W, x + w)):
        put(g, xx, y, c)

def vline(g, x, y, h, c):
    for yy in range(max(0, y), min(H, y + h)):
        put(g, x, yy, c)

# ---- expression pixel maps (screen-local 12x8, y0..7) ----
def expr_pixels(expr):
    if expr == 'open':
        return [(x, y) for x in (2, 3) for y in (1, 2, 3)] + \
               [(x, y) for x in (8, 9) for y in (1, 2, 3)]
    if expr == 'blink':
        return [(x, 2) for x in (2, 3)] + [(x, 2) for x in (8, 9)]
    if expr == 'happy':
        return [(2, 1), (3, 1), (2, 2), (8, 1), (9, 1), (9, 2),
                (4, 5), (5, 6), (6, 6), (7, 5)]
    if expr == 'wink':
        return [(x, y) for x in (2, 3) for y in (1, 2, 3)] + \
               [(8, 2), (9, 2), (4, 5), (5, 6), (6, 6), (7, 5)]
    if expr == 'x':
        return [(2, 1), (3, 2), (3, 1), (2, 2), (8, 1), (9, 2), (9, 1), (8, 2),
                (4, 6), (5, 5), (6, 5), (7, 6)]
    if expr == 'run':
        return [(2, 2), (3, 3), (8, 2), (9, 3), (4, 5), (5, 5), (6, 5), (7, 5)]
    if expr == 'shock':
        return [(2, 1), (2, 2), (2, 3), (9, 1), (9, 2), (9, 3), (5, 5), (6, 5)]
    if expr == 'dots':
        return [(2, 4), (5, 4), (8, 4)]
    if expr == 'q':
        return [(4, 1), (5, 1), (6, 1), (4, 2), (6, 2), (6, 3), (6, 4)]
    if expr == 'check':
        return [(2, 2), (3, 3), (4, 3), (5, 2), (6, 3), (7, 2), (8, 2), (8, 3), (9, 1)]
    if expr == 'qdots':
        return [(2, 2), (3, 2), (5, 2), (6, 2), (8, 2), (9, 2)]
    return []

# ---- drawing ----
def body_rects(bx, by, squash, stretch):
    """body width/height and re-centered origin given squash(>0 wider/shorter)
       and stretch(>0 taller/narrower)."""
    bw = 16 + squash - stretch
    bh = 14 - squash + stretch
    bxx = bx + (16 - bw) // 2
    byy = by + (14 - bh) // 2
    return bw, bh, bxx, byy

def draw_robot(g, dx=0, dy=0, lean=0, squash=0, stretch=0,
               armL=0, armR=0, footL=0, footR=0,
               antenna=1, shadow=True, dust=False, body_sink=0):
    bx = BASE_BX + dx
    by = BASE_BY + dy + body_sink
    bw, bh, bxx, byy = body_rects(bx, by, squash, stretch)

    # shadow under feet
    if shadow:
        sh_w = max(10, bw - 3 - max(0, -dy) * 1)
        rect(g, bx + (16 - sh_w) // 2, byy + bh + 2, sh_w, 2, SHAD)
    if dust:
        rect(g, bx - 1, 21, 2, 1, DUST)
        rect(g, bx + 15, 21, 2, 1, DUST)

    # antenna
    acx = bx + 7
    for yy in range(byy - 4, byy - 1):
        vline(g, acx + lean, yy, 1, BODY_M)
    tip = ANT if antenna else ANT_DM
    rect(g, acx - 1 + lean, byy - 6, 4, 2, tip)
    put(g, acx + lean, byy - 6, (255, 230, 130, 255) if antenna else (160, 140, 60, 255))

    # arms (side nubs). pose: 0 rest, 1 raised, 2 up-high, 3 forward-up
    def draw_arm(side, pose):
        x = (bx - 2) if side == 'L' else (bx + 16)
        if pose == 0:
            rect(g, x, byy + 2, 2, 3, BODY_M); put(g, x, byy + 2, BODY_L)
        elif pose == 1:
            rect(g, x, byy - 1, 2, 3, BODY_M); put(g, x, byy - 1, BODY_L)
        elif pose == 2:
            rect(g, x, byy - 6, 2, 4, BODY_M); put(g, x, byy - 6, BODY_L)
        elif pose == 3:
            rect(g, x, byy - 2, 2, 4, BODY_M); put(g, x, byy - 2, BODY_L)
    draw_arm('L', armL)
    draw_arm('R', armR)

    # feet
    def draw_foot(side, lifted):
        if lifted:
            return
        x = (bxx + 1) if side == 'L' else (bxx + bw - 5)
        rect(g, x, byy + bh, 4, 2, BODY_D)
        hline(g, x, byy + bh, 4, BODY_M)
    draw_foot('L', footL)
    draw_foot('R', footR)

    # body fill with shear (lean)
    for yy in range(byy, byy + bh):
        t = (byy + bh - 1 - yy) / max(1, bh - 1)
        xoff = round(lean * t)
        hline(g, bxx + xoff, yy, bw, BODY_M)
    # top highlight, bottom shade, left edge shade
    for i in range(bw):
        put(g, bxx + lean + i, byy, BODY_L)
        put(g, bxx + i, byy + bh - 1, BODY_D)
    for yy in range(byy + 1, byy + bh - 1):
        t = (byy + bh - 1 - yy) / max(1, bh - 1)
        put(g, bxx + round(lean * t), yy, BODY_D)
    # corner glints
    put(g, bxx + lean + 1, byy, BODY_L)
    put(g, bxx + lean + 2, byy, BODY_L)

def draw_screen(g, dx=0, dy=0, lean=0, squash=0, stretch=0, expr='open', body_sink=0):
    bx = BASE_BX + dx
    by = BASE_BY + dy + body_sink
    bw, bh, bxx, byy = body_rects(bx, by, squash, stretch)
    sw, shh = 12, 8
    sxx = bxx + (bw - sw) // 2
    syy = byy + 1
    # bezel
    rect(g, sxx - 1, syy - 1, sw + 2, shh + 2, OUT)
    # screen bg
    rect(g, sxx, syy, sw, shh, SCR_BG)
    # lit top+left strip
    hline(g, sxx, syy, sw, SCR_ON)
    vline(g, sxx, syy, shh, SCR_ON)
    # vent (speaker)
    vx = bxx + (bw - 4) // 2
    rect(g, vx, byy + 10, 4, 2, OUT)
    put(g, vx + 1, byy + 10, BODY_M)
    # expression
    for (sx, sy) in expr_pixels(expr):
        put(g, sxx + sx, syy + sy, EYE)

def render_frame(dx=0, dy=0, lean=0, squash=0, stretch=0,
                 armL=0, armR=0, footL=0, footR=0,
                 expr='open', antenna=1, shadow=True, dust=False, body_sink=0):
    g = new_cell()
    draw_robot(g, dx, dy, lean, squash, stretch, armL, armR, footL, footR,
               antenna, shadow, dust, body_sink)
    draw_screen(g, dx, dy, lean, squash, stretch, expr, body_sink)
    img = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
    p = img.load()
    for y in range(H):
        for x in range(W):
            c = g[y][x]
            if c is None:
                continue
            for yy in range(PX):
                for xx in range(PX):
                    p[x * PX + xx, y * PX + yy] = c
    return img

# ---- state frame specs ----
def spec_idle():
    return [
        dict(dy=0, expr='open'),
        dict(dy=-1, expr='blink'),
        dict(dy=-1, expr='open'),
        dict(dy=-2, expr='open', antenna=2),
        dict(dy=-1, expr='open'),
        dict(dy=0, expr='open'),
    ]

def spec_run(dxs, dys, n, lean):
    feet = [(0, 1), (1, 0), (0, 1), (1, 0)]   # (left,right) lifted
    idx = [0, 1, 3, 5, 6, 7] if n == 6 else range(n)
    out = []
    for i in idx:
        fl, fr = feet[i // 2 % 4]
        out.append(dict(dx=dxs[i], dy=dys[i], expr='run', lean=lean,
                        footL=fl, footR=fr))
    return out

def spec_wave():
    return [dict(expr='happy', armR=3),
            dict(expr='happy', armR=2),
            dict(expr='happy', armR=3),
            dict(expr='happy', armR=3)]

def spec_jump():
    return [
        dict(dy=0, expr='open', squash=1, dust=True),
        dict(dy=-2, expr='shock', stretch=1, footL=1, footR=1),
        dict(dy=-3, expr='shock', stretch=2, footL=1, footR=1, antenna=2),
        dict(dy=-2, expr='open', stretch=1, footL=1, footR=1),
        dict(dy=0, expr='happy', squash=2, dust=True),
    ]

def spec_failed():
    dxs = [0, 1, 0, -1, 0, 1, 0, 0]
    ants = [1, 0, 1, 0, 1, 1, 0, 0]
    return [dict(dx=dxs[i], dy=1, body_sink=1, expr='x', antenna=ants[i])
            for i in range(8)]

def spec_waiting():
    dxs = [0, 1, 1, 0, -1, -1]
    exprs = ['open', 'dots', 'dots', 'open', 'dots', 'dots']
    return [dict(dx=dxs[i], expr=exprs[i]) for i in range(6)]

def spec_review():
    exprs = ['q', 'qdots', 'check', 'check', 'dots', 'q']
    leans = [1, 1, 0, 0, 0, -1]
    ants = [1, 1, 2, 2, 1, 1]
    return [dict(expr=exprs[i], lean=leans[i], antenna=ants[i]) for i in range(6)]

def build_spritesheet():
    rx = [0, 1, 2, 2, 1, 0, -1, -1]
    ry = [0, -1, -1, 0, 0, -1, -1, 0]
    states = [
        ('idle', spec_idle()),
        ('running-right', spec_run(rx, ry, 8, 1)),
        ('running-left', spec_run([-v for v in rx], ry, 8, -1)),
        ('waving', spec_wave()),
        ('jumping', spec_jump()),
        ('failed', spec_failed()),
        ('waiting', spec_waiting()),
        ('running', spec_run(rx, ry, 6, 1)),
        ('review', spec_review()),
    ]
    sheet = Image.new('RGBA', (NCOLS * CELL_W, NROWS * CELL_H), (0, 0, 0, 0))
    for r, (name, frames) in enumerate(states):
        for c, sp in enumerate(frames):
            img = render_frame(**sp)
            sheet.paste(img, (c * CELL_W, r * CELL_H), img)
        print(f"row {r}: {name}: {len(frames)} frames")
    return sheet

if __name__ == '__main__':
    sheet = build_spritesheet()
    out = r"C:\Users\xhr\Documents\Codex\2026-08-13\bitty\spritesheet.png"
    sheet.save(out)
    print("saved", out, sheet.size)
