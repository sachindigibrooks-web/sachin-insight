# Background removal with BiRefNet (MIT licence, ZhengPeng7/BiRefNet on HuggingFace).
import sys
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

model = AutoModelForImageSegmentation.from_pretrained('ZhengPeng7/BiRefNet', trust_remote_code=True).eval()
tf = transforms.Compose([transforms.Resize((1024, 1024)), transforms.ToTensor(),
                         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
for path in sys.argv[1:]:
    im = Image.open(path).convert('RGB')
    with torch.no_grad():
        pred = model(tf(im).unsqueeze(0))[-1].sigmoid()[0, 0].numpy()
    mask = Image.fromarray((pred * 255).astype(np.uint8)).resize(im.size, Image.BILINEAR)
    out = im.convert('RGBA')
    out.putalpha(mask)
    out = out.crop(mask.point(lambda v: 255 if v > 20 else 0).getbbox())
    out.save(path)
    print(path, out.size)
