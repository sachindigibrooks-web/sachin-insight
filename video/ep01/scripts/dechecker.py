# Removes a baked-in transparency checkerboard: flood-fills from the borders through pixels that match
# the checker colours, makes them transparent, and feathers the edge by 1px.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

for path in sys.argv[1:]:
    a = np.array(Image.open(path).convert('RGBA')).astype(int)
    rgb = a[..., :3]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    cols, counts = np.unique(border, axis=0, return_counts=True)
    checker = cols[np.argsort(-counts)[:2]]
    match = np.zeros(rgb.shape[:2], bool)
    for c in checker:
        match |= (np.abs(rgb - c).max(-1) <= 6)
    lab, _ = ndimage.label(match)
    edge_labels = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge_labels[edge_labels > 0])
    bg = ndimage.binary_opening(bg, iterations=1) | bg
    alpha = np.where(bg, 0, 255).astype(float)
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    a[..., 3] = alpha.clip(0, 255)
    im = Image.fromarray(a.astype(np.uint8))
    im = im.crop(im.getbbox())
    im.save(path)
    print(path, checker.tolist(), im.size, f'{bg.mean()*100:.0f}% bg')
