# Hollow Knight "The Knight" (小骑士) pet spritesheet generator
# Grid: 8 cols x 9 rows, cells 192x208, spritesheet 1536x1872
# Logical grid per cell: 24 x 26, pixel scale PX=8
# State rows (app-hardcoded): 0 idle(6f, 6x slow), 1 run-right(8f), 2 run-left(8f),
#   3 waving(4f), 4 jumping(5f), 5 failed(8f), 6 waiting(6f), 7 running(6f), 8 review(6f)

from PIL import Image

# ---- palette (RGBA) ----
MASK      = (252, 249, 240, 255)   # bone-white mask
MASK_SH   = (225, 218, 205, 255)   # mask shadow side
MASK_DK   = (120, 110, 100, 255)   # mask soft outline
EYE       = (18, 14, 18, 255)      # black void eyes
BODY      = (48, 40, 44, 255)      # dark charcoal body
BODY_D    = (26, 21, 25, 255)      # body shadow / outline
BODY_L    = (96, 86, 92, 255)      # body highlight
NAIL      = (198, 205, 218, 255)   # silver blade
NAIL_SH   = (238, 244, 255, 255)   # blade shine
NAIL_D    = (118, 124, 138, 255)   # guard / dark steel
HANDLE    = (104, 88, 78, 255)     # wooden handle
STAR      = (255, 222, 96, 255)    # dizzy star gold
STAR_DM   = (196, 150, 54, 255)    # star dim
DUST      = (190, 185, 178, 255)   # impact dust
SHAD      = (12, 10, 14, 80)       # translucent ground shadow

W, H = 24, 26
PX = 8
CELL_W, CELL_H = 192, 208
NCOLS, NROWS = 8, 9

# figure layout (logical px)
HEAD_X, HEAD_W = 6, 13          # mask x6..18
HEAD_H, BODY_H, FEET_H = 9, 5, 2
BOTTOM = 19                     # feet bottom row (feet y18..19)
CX = 12                         # cell center x

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

def rr_mask(x, y, w, h, r):
    """rounded-rect pixel set"""
    m = set()
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            dx = min(xx - x, (x + w - 1) - xx)
            dy = min(yy - y, (y + h - 1) - yy)
            if dx < r and dy < r and dx + dy < r:
                continue
            m.add((xx, yy))
    return m

def outline(g, mask, col):
    """outline every mask pixel whose 4-neighbor is outside the mask"""
    for (xx, yy) in mask:
        if ((xx - 1, yy) not in mask or (xx + 1, yy) not in mask or
                (xx, yy - 1) not in mask or (xx, yy + 1) not in mask):
            g[yy][xx] = col

def shear_grid(g, lean):
    """shear whole figure: rows near top shift by lean (positive = lean right)"""
    if lean == 0:
        return g
    out = new_cell()
    for y in range(H):
        shift = round(lean * (BOTTOM - y) / 8.0)
        for x in range(W):
            c = g[y][x]
            if c is not None and 0 <= x + shift < W:
                out[y][x + shift] = c
    return out

# ---- expressions (eyes) ----
# eye base rects are 4 wide x 5 tall; base_y = head_y + 2
def expr_pixels(expr, lx, rx, y):
    LE = (lx, lx + 1, lx + 2, lx + 3)
    RE = (rx, rx + 1, rx + 2, rx + 3)
    if expr == 'open':
        return [(x, yy) for x in LE for yy in range(y, y + 5)] + \
               [(x, yy) for x in RE for yy in range(y, y + 5)]
    if expr == 'blink':
        return [(x, y + 2) for x in LE] + [(x, y + 2) for x in RE]
    if expr == 'squint':
        return [(x, yy) for x in LE for yy in (y + 1, y + 2)] + \
               [(x, yy) for x in RE for yy in (y + 1, y + 2)]
    if expr == 'happy':
        return [(lx, y + 3), (lx + 1, y + 2), (lx + 2, y + 2), (lx + 3, y + 3),
                (rx, y + 3), (rx + 1, y + 2), (rx + 2, y + 2), (rx + 3, y + 3)]
    if expr == 'wink':
        return [(x, yy) for x in LE for yy in range(y, y + 5)] + \
               [(x, y + 2) for x in RE]
    if expr == 'x':
        return [(lx, y), (lx + 3, y + 4), (lx + 3, y), (lx, y + 4),
                (lx + 1, y + 2), (lx + 2, y + 3), (lx + 2, y + 2), (lx + 1, y + 3),
                (rx, y), (rx + 3, y + 4), (rx + 3, y), (rx, y + 4),
                (rx + 1, y + 2), (rx + 2, y + 3), (rx + 2, y + 2), (rx + 1, y + 3)]
    if expr == 'small':
        return [(x, yy) for x in (lx + 1, lx + 2) for yy in (y + 2, y + 3)] + \
               [(x, yy) for x in (rx + 1, rx + 2) for yy in (y + 2, y + 3)]
    return []

# ---- drawing ----
def draw_horns(g, hy):
    """two pointed horns on top of the mask; hy = head top row"""
    hb = hy - 3                       # horn base rows hy-3..hy-1
    left = [(7, hb), (7, hb + 1), (8, hb + 1), (7, hb + 2), (8, hb + 2)]
    right = [(16, hb), (16, hb + 1), (15, hb + 1), (16, hb + 2), (15, hb + 2)]
    allh = set(left + right)
    for (xx, yy) in left + right:
        if 0 <= yy < H and 0 <= xx < W:
            g[yy][xx] = MASK
    # outline the horn silhouette
    for (xx, yy) in allh:
        if ((xx - 1, yy) not in allh or (xx + 1, yy) not in allh or
                (xx, yy - 1) not in allh or (xx, yy + 1) not in allh):
            g[yy][xx] = MASK_DK
    # inner highlight on each horn
    put(g, 8, hb + 1, MASK)
    put(g, 15, hb + 1, MASK)

def draw_head(g, hy, hh, expr):
    """mask + horns + eyes. hy = head top, hh = head height."""
    m = rr_mask(HEAD_X, hy, HEAD_W, hh, 2)
    for (xx, yy) in m:
        g[yy][xx] = MASK
    # shading: bottom row + right column of the mask
    for (xx, yy) in m:
        if (xx, yy + 1) not in m:
            g[yy][xx] = MASK_SH
        elif (xx + 1, yy) not in m:
            g[yy][xx] = MASK_SH
    outline(g, m, MASK_DK)
    draw_horns(g, hy)
    # eyes (base 4 wide x 5 tall)
    ey = hy + 2
    if expr == 'shock':
        lx, rx = 7, 13                 # bigger eye rects for shock
        px = [(x, yy) for x in range(lx, lx + 5) for yy in range(hy + 1, hy + 7)] + \
             [(x, yy) for x in range(rx, rx + 5) for yy in range(hy + 1, hy + 7)]
    else:
        lx, rx = 7, 13
        px = expr_pixels(expr, lx, rx, ey)
    for (xx, yy) in px:
        put(g, xx, yy, EYE)

def draw_body(g, hy, hh, bh, footL, footR):
    body_y = hy + hh
    body_x, body_w = 10, 6
    # body fill (rounded top corners)
    m = rr_mask(body_x, body_y, body_w, bh, 1)
    for (xx, yy) in m:
        g[yy][xx] = BODY
    # highlight top, shadow bottom
    for xx in range(body_x, body_x + body_w):
        if (xx, body_y) in m:
            g[body_y][xx] = BODY_L
    for xx in range(body_x, body_x + body_w):
        if (xx, body_y + bh - 1) in m:
            g[body_y + bh - 1][xx] = BODY_D
    # feet nubs (1px gap between them)
    fy = body_y + bh
    if not footL:
        rect(g, 10, fy, 2, FEET_H, BODY_D)
    if not footR:
        rect(g, 13, fy, 2, FEET_H, BODY_D)

def draw_nail(g, guard_y):
    """the Knight's nail held beside the body; guard_y = y of the cross-guard"""
    # blade
    for yy in range(guard_y - 8, guard_y):
        put(g, 20, yy, NAIL_SH)
        put(g, 21, yy, NAIL)
    put(g, 21, guard_y - 9, NAIL)      # tip
    # cross guard
    for xx in range(19, 23):
        put(g, xx, guard_y, NAIL_D)
    # handle + pommel
    for yy in range(guard_y + 2, guard_y + 6):
        put(g, 21, yy, HANDLE)
    put(g, 21, guard_y + 6, NAIL_D)
    # paw gripping above the guard
    put(g, 20, guard_y + 1, BODY_D)
    put(g, 21, guard_y + 1, BODY_D)

def draw_shadow(g, cx, shrink=0):
    w = 10 - shrink
    rect(g, cx - w // 2, BOTTOM + 2, w, 1, SHAD)
    rect(g, cx - w // 2 + 1, BOTTOM + 3, w - 2, 1, SHAD)

def draw_dust(g):
    put(g, 9, BOTTOM + 1, DUST)
    put(g, 15, BOTTOM + 1, DUST)
    put(g, 10, BOTTOM + 2, DUST)
    put(g, 14, BOTTOM + 2, DUST)

def draw_star(g, on):
    if not on:
        return
    for (sx, sy, c) in [(11, 1, STAR), (12, 1, STAR), (11, 2, STAR), (12, 2, STAR),
                        (11, 0, STAR_DM), (10, 1, STAR_DM), (13, 1, STAR_DM), (12, 0, STAR_DM),
                        (11, 3, STAR_DM), (10, 2, STAR_DM), (13, 2, STAR_DM), (12, 3, STAR_DM)]:
        put(g, sx, sy, c)

def render_frame(dx=0, dy=0, lean=0, squash=0, stretch=0,
                 expr='open', footL=0, footR=0, nraise=0, dust=False, star=False):
    g = new_cell()
    hh = HEAD_H                      # head height fixed; squash/stretch move body
    bh = BODY_H - squash + stretch
    hy = BOTTOM - FEET_H - bh - hh + dy

    draw_head(g, hy, hh, expr)
    draw_body(g, hy, hh, bh, footL, footR)
    guard_y = 15 - nraise
    draw_nail(g, guard_y)

    g = shear_grid(g, lean)

    # ground effects (not sheared)
    shrink = 3 if dy < 0 else 0
    draw_shadow(g, CX + dx, shrink)
    if dust:
        draw_dust(g)
    draw_star(g, star)

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
        dict(expr='open'),
        dict(expr='blink'),
        dict(dy=-1, expr='open'),
        dict(dy=-1, expr='open', lean=1),
        dict(expr='open'),
        dict(expr='open'),
    ]

def spec_run_right():
    dxs = [0, 1, 2, 2, 1, 0, -1, -1]
    dys = [0, -1, -1, 0, 0, -1, -1, 0]
    out = []
    for i in range(8):
        liftL = i // 2 % 2 == 0
        out.append(dict(dx=dxs[i], dy=dys[i], lean=1, expr='squint',
                        footL=liftL, footR=not liftL))
    return out

def spec_run_left():
    dxs = [0, -1, -2, -2, -1, 0, 1, 1]
    dys = [0, -1, -1, 0, 0, -1, -1, 0]
    out = []
    for i in range(8):
        liftL = i // 2 % 2 == 0
        out.append(dict(dx=dxs[i], dy=dys[i], lean=-1, expr='squint',
                        footL=liftL, footR=not liftL))
    return out

def spec_wave():
    return [
        dict(expr='happy'),
        dict(dy=-1, expr='happy', nraise=3),
        dict(dy=-1, lean=1, expr='happy', nraise=5),
        dict(dy=0, lean=-1, expr='happy', nraise=5),
    ]

def spec_jump():
    return [
        dict(squash=1, expr='open', dust=True),                          # crouch
        dict(stretch=1, dy=-1, expr='shock', nraise=2, footL=1, footR=1),   # launch
        dict(stretch=1, dy=-2, expr='happy', nraise=3, footL=1, footR=1),   # apex
        dict(stretch=1, dy=-1, expr='shock', nraise=2, footL=1, footR=1),   # descend
        dict(squash=2, expr='open', dust=True),                          # land
    ]

def spec_failed():
    leans = [0, 1, 0, -1, 0, 1, 0, -1]
    dxs = [0, 1, 0, -1, 0, 1, 0, 0]
    stars = [0, 1, 1, 1, 1, 1, 1, 0]
    return [dict(dx=dxs[i], lean=leans[i], squash=1, expr='x', star=stars[i])
            for i in range(8)]

def spec_waiting():
    return [
        dict(expr='small', footR=1),
        dict(dy=-1, expr='small', footR=1),
        dict(expr='small', footL=1),
        dict(dy=-1, expr='small', footL=1),
        dict(expr='open'),
        dict(expr='blink'),
    ]

def spec_running():
    # 6-frame run (app plays this subset of the 8-frame run)
    rx = [0, 1, 2, 2, 1, 0, -1, -1]
    ry = [0, -1, -1, 0, 0, -1, -1, 0]
    idx = [0, 1, 3, 5, 6, 7]
    out = []
    for i in idx:
        liftL = i // 2 % 2 == 0
        out.append(dict(dx=rx[i], dy=ry[i], lean=1, expr='squint',
                        footL=liftL, footR=not liftL))
    return out

def spec_review():
    leans = [-1, -1, 1, 1, -1, 0]
    exprs = ['squint', 'open', 'squint', 'open', 'squint', 'blink']
    return [dict(lean=leans[i], expr=exprs[i], nraise=2) for i in range(6)]

def build_spritesheet():
    states = [
        ('idle', spec_idle()),
        ('running-right', spec_run_right()),
        ('running-left', spec_run_left()),
        ('waving', spec_wave()),
        ('jumping', spec_jump()),
        ('failed', spec_failed()),
        ('waiting', spec_waiting()),
        ('running', spec_running()),
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
    out = r"C:\Users\xhr\Documents\Codex\2026-08-14\hollowknight\spritesheet.png"
    sheet.save(out)
    print("saved", out, sheet.size)
