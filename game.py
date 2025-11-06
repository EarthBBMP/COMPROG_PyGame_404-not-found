import pygame, sys, math
pygame.init()

W, H = 900, 520
scr = pygame.display.set_mode((W, H))
clk = pygame.time.Clock()
F = pygame.font.SysFont(None, 28)
G = pygame.font.SysFont(None, 36)

# player
pw, ph = 42, 54
gy = int(H * 0.6)
px, py = 0.0, gy - ph
spd = 6

# world
T = 60
objs = [
    {"name": "Board", "rect": pygame.Rect(300, gy - 50, 40, 50)},
    {"name": "Mailbox", "rect": pygame.Rect(900, gy - 50, 40, 50)},
    {"name": "Crystal", "rect": pygame.Rect(1600, gy - 70, 40, 70)},
]

rng = 70

# ui
q = False # quest open?
tgt = None # current target
e_lock = False # debounce E

def bg(cam):
    p = 0.4
    off = -int(cam * p) % W
    g = pygame.Surface((W, H))
    for y in range(H):
        s = 20 + int((y / H) * 20)
        pygame.draw.line(g, (s, s, s + 10), (0, y), (W, y))
    scr.blit(g, (off - W, 0))
    scr.blit(g, (off, 0))
    pygame.draw.rect(scr, (40, 40, 45), (0, gy, W, H - gy))

def w2s(x, y, cam): # world->screen
    return int(x - cam + W // 2), int(y)

def draw_objs(cam):
    for o in objs:
        sx, sy = w2s(o["rect"].x, o["rect"].y, cam)
        r = pygame.Rect(sx, sy, o["rect"].w, o["rect"].h)
        pygame.draw.rect(scr, (180, 120, 80), r)
        label = F.render(o["name"], True, (230, 230, 230))
        scr.blit(label, (r.centerx - label.get_width() // 2, r.y - 22))

def nearest(px_world):
    best, dmin = None, 1e9
    for o in objs:
        cx, cy = o["rect"].center
        d = math.hypot(px_world - cx, (py + ph / 2) - cy)
        if d < dmin:
            best, dmin = o, d
    return best, dmin

def draw_player(cam):
    sx, sy = w2s(px, py, cam)
    pygame.draw.rect(scr, (0, 200, 255), (sx, sy, pw, ph))

def hud(cam):
    bar = pygame.Surface((W, 30), pygame.SRCALPHA); bar.fill((0, 0, 0, 120))
    scr.blit(bar, (0, 0))
    scr.blit(F.render(f"x={int(px)}", True, (240, 240, 240)), (12, 6))
    o, d = nearest(px + pw / 2)
    if o and d <= rng and not q:
        hint = F.render(f"[E] {o['name']}", True, (255, 255, 255))
        scr.blit(hint, (W // 2 - hint.get_width() // 2, 6))

def quest():
    dim = pygame.Surface((W, H), pygame.SRCALPHA); dim.fill((0, 0, 0, 150))
    scr.blit(dim, (0, 0))
    w, h = int(W * 0.6), int(H * 0.55)
    x, y = (W - w) // 2, (H - h) // 2
    p = pygame.Rect(x, y, w, h)
    pygame.draw.rect(scr, (235, 235, 240), p, border_radius=16)
    pygame.draw.rect(scr, (40, 40, 45), p, 4, border_radius=16)
    scr.blit(G.render("Quest", True, (20, 20, 28)), (p.centerx - 40, p.y + 18))
    lines = [
        f"Target: {tgt['name']}" if tgt else "No target",
        "• Explore",
        "• Find crystal",
        "• Return to board",
        "E/Esc: close",
    ]
    yy = y + 70
    for s in lines:
        scr.blit(F.render(s, True, (35, 35, 45)), (x + 28, yy)); yy += 32

cam = 0.0
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_e and not e_lock:
                e_lock = True
                if q:
                    q, tgt = False, None
                else:
                    o, d = nearest(px + pw / 2)
                    if o and d <= rng:
                        q, tgt = True, o
            if e.key == pygame.K_ESCAPE and q:
                q, tgt = False, None
        if e.type == pygame.KEYUP and e.key == pygame.K_e:
            e_lock = False

    keys = pygame.key.get_pressed()
    if not q:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: px -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px += spd

    cam = px
    bg(cam); draw_objs(cam); draw_player(cam); hud(cam)
    if q: quest()
    pygame.display.flip()
    clk.tick(60)