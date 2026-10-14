# Procedural background textures (top-down desk surfaces, paper, grids) in the EarnEdits collage style.
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter
rng = np.random.default_rng(7)
W, H = 1240, 2200

def noise(h, w, sigma):
    return gaussian_filter(rng.standard_normal((h, w)), sigma)

def norm(a):
    a = a - a.min(); return a / (a.max() + 1e-9)

def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(f"public/tex/{name}.png", optimize=True)

def vignette(h, w, strength):
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    return 1 - strength * np.clip(d - 0.35, 0, 1) ** 1.6

# Walnut wood planks, running vertically
y, x = np.mgrid[0:H, 0:W].astype(float)
plank_w = 248
pid = (x // plank_w).astype(int)
offs = rng.uniform(0, 1000, 10)[pid]
warp = noise(H, W, 40) * 60
grain = np.sin((x + warp + offs) * 0.09 + noise(H, W, 6) * 3) * 0.5 + 0.5
fine = norm(gaussian_filter(rng.standard_normal((H, W)), (12, 0.6)))
tone = 0.55 + 0.45 * (0.6 * grain + 0.4 * fine)
tone *= rng.uniform(0.82, 1.08, 10)[pid]
seam = (np.abs((x % plank_w) - 0) < 3) | (np.abs((x % plank_w) - plank_w) < 3)
tone[seam] *= 0.35
v = vignette(H, W, 0.8)
base = np.array([92, 58, 34]); hi = np.array([150, 100, 62])
img = (base + (hi - base) * tone[..., None]) * (tone[..., None] * 0.5 + 0.6) * v[..., None]
save(img, "wood")

# White grid paper (blueprint table)
img = np.full((H, W, 3), 238.0)
img += noise(H, W, 30)[..., None] * 40 + noise(H, W, 1)[..., None] * 6
g = 62
minor = ((x % g) < 2) | ((y % g) < 2)
major = ((x % (g * 4)) < 3) | ((y % (g * 4)) < 3)
img[minor] -= [40, 30, 14]
img[major] -= [70, 52, 22]
img *= vignette(H, W, 0.55)[..., None]
save(img, "grid")

# Green self-healing cutting mat
img = np.zeros((H, W, 3)) + [38, 92, 58]
img += noise(H, W, 2)[..., None] * 10 + noise(H, W, 50)[..., None] * 25
g = 70
img[((x % g) < 2) | ((y % g) < 2)] += [40, 60, 40]
img[((x % (g * 5)) < 4) | ((y % (g * 5)) < 4)] += [70, 90, 70]
img *= vignette(H, W, 0.7)[..., None]
save(img, "mat")

# Blue felt desk
img = np.zeros((H, W, 3)) + [40, 78, 150]
f = noise(H, W, 0.8) * 22 + noise(H, W, 18) * 30
img += f[..., None] * [0.5, 0.7, 1.0]
img *= vignette(H, W, 0.75)[..., None]
save(img, "blue")

# Charcoal studio backdrop
img = np.zeros((H, W, 3)) + [30, 30, 34]
img += noise(H, W, 1)[..., None] * 8 + noise(H, W, 60)[..., None] * 18
y0 = np.exp(-(((x - W / 2) / 650) ** 2 + ((y - H * 0.42) / 900) ** 2))
img += y0[..., None] * [34, 32, 30]
img *= vignette(H, W, 0.6)[..., None]
save(img, "dark")

# Red velvet stage-ish backdrop for the ZERO beat
img = np.zeros((H, W, 3)) + [70, 10, 12]
folds = np.sin(x / 38 + noise(H, W, 80) * 4) * 0.5 + 0.5
img += folds[..., None] * [70, 10, 10]
img *= vignette(H, W, 0.9)[..., None]
save(img, "red")

# Aged paper (cards, newspaper)
PW, PH = 900, 1200
yy, xx = np.mgrid[0:PH, 0:PW]
p = np.zeros((PH, PW, 3)) + [236, 228, 208]
p += gaussian_filter(rng.standard_normal((PH, PW)), 40)[..., None] * [60, 55, 40]
p += gaussian_filter(rng.standard_normal((PH, PW)), 0.7)[..., None] * 7
for _ in range(14):
    cx, cy, r = rng.uniform(0, PW), rng.uniform(0, PH), rng.uniform(30, 160)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    p -= (np.exp(-((d - r) / 3) ** 2) * 10)[..., None] * [0.6, 0.9, 1.4]
save(p, "paper")

# Newsprint
p = np.zeros((PH, PW, 3)) + [226, 222, 212]
p += gaussian_filter(rng.standard_normal((PH, PW)), 25)[..., None] * 18
p += gaussian_filter(rng.standard_normal((PH, PW)), 0.6)[..., None] * 9
save(p, "newsprint")
print("ok")
