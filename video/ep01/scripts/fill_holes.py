# Makes enclosed see-through areas of a cutout opaque again (white engraving fill), or tints them as glass.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

mode = sys.argv[1]
for path in sys.argv[2:]:
    a = np.array(Image.open(path).convert('RGBA')).astype(float)
    solid = a[..., 3] > 110
    filled = ndimage.binary_fill_holes(ndimage.binary_closing(solid, iterations=3))
    holes = filled & ~solid
    if mode == 'solid':
        a[..., 3] = np.where(filled, np.maximum(a[..., 3], 255 * ndimage.gaussian_filter(filled.astype(float), 0.6)), a[..., 3])
    else:  # glass
        a[holes, :3] = [205, 235, 250]
        a[holes, 3] = 90
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(path)
    print(path, f'{holes.mean()*100:.1f}% filled')
