"""Generate notebooks/ltx_video_colab.ipynb.

Run: python notebooks/build_ltx_video_colab.py  (needs `pip install nbformat`)
Edit the cells here, not the .ipynb, so the notebook stays reproducible.
"""

from pathlib import Path

import nbformat as nbf

INTRO = """\
# LTX-Video on free Google Colab (text-to-video + image-to-video)

Generates short AI video clips with [Lightricks/LTX-Video](https://huggingface.co/Lightricks/LTX-Video)
(2B model, open weights) on Colab's **free T4 GPU**.

**How to use**
1. `Runtime` → `Change runtime type` → select **T4 GPU** → Save.
2. Run the cells from top to bottom (`Runtime` → `Run all`).
3. Change the prompt in the *Text-to-video* cell and re-run only that cell for new videos.

**Good to know**
- The first run downloads ~28 GB of model weights (around 10–15 minutes). They are deleted
  when the Colab session ends, so a new session downloads them again.
- On a T4, one 4-second 704×480 clip takes a few minutes.
- Width and height must be multiples of 32. Frame count must be `8 × n + 1` (for example 65, 97, 121).
- LTX-Video works best with long, detailed prompts that describe the scene, motion, camera and lighting.
"""

GPU_CHECK = """\
#@title 1. Check the GPU
import torch

assert torch.cuda.is_available(), (
    "No GPU found. Go to Runtime -> Change runtime type -> T4 GPU, then run this cell again."
)
!nvidia-smi --query-gpu=name,memory.total --format=csv
"""

INSTALL = """\
#@title 2. Install libraries (about 1 minute)
!pip install -q -U "diffusers>=0.41" "transformers>=4.46" "accelerate>=1.1" "bitsandbytes>=0.48" \\
    sentencepiece imageio imageio-ffmpeg
"""

LOAD = """\
#@title 3. Load the model (first run downloads ~28 GB)
import gc
import torch
from diffusers import LTXPipeline, LTXVideoTransformer3DModel
from transformers import BitsAndBytesConfig, T5EncoderModel

MODEL_ID = "Lightricks/LTX-Video"

# T4 has no native bfloat16, so use float16 there; A100/L4 and newer get bfloat16.
# If videos come out black or noisy on a T4, set FORCE_BF16 = True (slower, emulated).
FORCE_BF16 = False  #@param {type:"boolean"}
major, _ = torch.cuda.get_device_capability()
DTYPE = torch.bfloat16 if (major >= 8 or FORCE_BF16) else torch.float16
print(f"GPU: {torch.cuda.get_device_name()} | dtype: {DTYPE}")

# The T5 text encoder is ~19 GB in float32. Loading it in 8-bit straight onto the GPU keeps
# Colab's ~12 GB of system RAM from running out.
text_encoder = T5EncoderModel.from_pretrained(
    MODEL_ID,
    subfolder="text_encoder",
    quantization_config=BitsAndBytesConfig(load_in_8bit=True),
    torch_dtype=torch.float16,
    device_map={"": 0},
)
transformer = LTXVideoTransformer3DModel.from_pretrained(
    MODEL_ID, subfolder="transformer", torch_dtype=DTYPE
)
pipe = LTXPipeline.from_pretrained(
    MODEL_ID, text_encoder=text_encoder, transformer=transformer, torch_dtype=DTYPE
)
pipe.to("cuda")
pipe.vae.enable_tiling()  # decode the video in tiles to save GPU memory

gc.collect()
torch.cuda.empty_cache()
print(f"Model ready. GPU memory used: {torch.cuda.memory_allocated() / 1e9:.1f} GB")
"""

HELPERS = """\
#@title 4. Helpers (save + show videos)
import base64
import os
import time

from diffusers.utils import export_to_video
from IPython.display import HTML, display

OUTPUT_DIR = "/content/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def check_size(width, height, num_frames):
    if width % 32 or height % 32:
        raise ValueError(f"Width and height must be multiples of 32 (got {width}x{height}).")
    if (num_frames - 1) % 8:
        raise ValueError(f"num_frames must be 8*n + 1, e.g. 65, 97, 121 (got {num_frames}).")


def save_and_show(frames, name, fps):
    path = os.path.join(OUTPUT_DIR, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
    export_to_video(frames, path, fps=fps)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    display(HTML(f'<video width="640" controls loop autoplay muted>'
                 f'<source src="data:video/mp4;base64,{data}" type="video/mp4"></video>'))
    print("Saved:", path)
    return path
"""

NEGATIVE = (
    "worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text, logo"
)

T2V = f"""\
#@title 5. Text-to-video
prompt = "A golden retriever runs across a sunlit meadow toward the camera, ears flapping, tall grass swaying in the breeze. The camera tracks backward at ground level. Warm late-afternoon light, shallow depth of field, cinematic, highly detailed."  #@param {{type:"string"}}
negative_prompt = "{NEGATIVE}"  #@param {{type:"string"}}
width = 704  #@param {{type:"integer"}}
height = 480  #@param {{type:"integer"}}
num_frames = 97  #@param {{type:"integer"}}
fps = 24  #@param {{type:"integer"}}
num_inference_steps = 40  #@param {{type:"slider", min:10, max:60, step:1}}
guidance_scale = 3.0  #@param {{type:"number"}}
seed = 42  #@param {{type:"integer"}}

check_size(width, height, num_frames)
start = time.time()
frames = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    width=width,
    height=height,
    num_frames=num_frames,
    frame_rate=fps,
    num_inference_steps=num_inference_steps,
    guidance_scale=guidance_scale,
    decode_timestep=0.03,
    decode_noise_scale=0.025,
    generator=torch.Generator(device="cuda").manual_seed(seed),
).frames[0]
print(f"Generated {{len(frames)}} frames in {{time.time() - start:.0f}} s")
t2v_path = save_and_show(frames, "t2v", fps)
"""

I2V = f"""\
#@title 6. Image-to-video (optional)
#@markdown Animates a starting image. Leave `image_url` empty to upload a file from your computer.
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import load_image

image_url = ""  #@param {{type:"string"}}
prompt = "The camera slowly pushes in while the subject turns their head and smiles. Soft natural light, gentle breeze, cinematic, highly detailed."  #@param {{type:"string"}}
negative_prompt = "{NEGATIVE}"  #@param {{type:"string"}}
width = 704  #@param {{type:"integer"}}
height = 480  #@param {{type:"integer"}}
num_frames = 97  #@param {{type:"integer"}}
fps = 24  #@param {{type:"integer"}}
num_inference_steps = 40  #@param {{type:"slider", min:10, max:60, step:1}}
guidance_scale = 3.0  #@param {{type:"number"}}
seed = 42  #@param {{type:"integer"}}

if image_url:
    image = load_image(image_url)
else:
    from google.colab import files
    uploaded = files.upload()
    image = load_image(next(iter(uploaded)))
image = image.convert("RGB").resize((width, height))

# Reuses the models already on the GPU; nothing is downloaded again.
i2v_pipe = LTXImageToVideoPipeline.from_pipe(pipe)

check_size(width, height, num_frames)
start = time.time()
frames = i2v_pipe(
    image=image,
    prompt=prompt,
    negative_prompt=negative_prompt,
    width=width,
    height=height,
    num_frames=num_frames,
    frame_rate=fps,
    num_inference_steps=num_inference_steps,
    guidance_scale=guidance_scale,
    decode_timestep=0.03,
    decode_noise_scale=0.025,
    generator=torch.Generator(device="cuda").manual_seed(seed),
).frames[0]
print(f"Generated {{len(frames)}} frames in {{time.time() - start:.0f}} s")
i2v_path = save_and_show(frames, "i2v", fps)
"""

SAVE = """\
#@title 7. Save videos (optional)
#@markdown `drive` copies every video to Google Drive (`MyDrive/ltx-video`); `download` downloads them to your computer.
destination = "drive"  #@param ["drive", "download"]
import glob
import shutil

videos = sorted(glob.glob(f"{OUTPUT_DIR}/*.mp4"))
if destination == "drive":
    from google.colab import drive
    drive.mount("/content/drive")
    target = "/content/drive/MyDrive/ltx-video"
    os.makedirs(target, exist_ok=True)
    for v in videos:
        shutil.copy(v, target)
    print(f"Copied {len(videos)} video(s) to {target}")
else:
    from google.colab import files
    for v in videos:
        files.download(v)
"""

TIPS = """\
## Troubleshooting
- **`CUDA out of memory`**: lower `num_frames` (e.g. 65) or the resolution (e.g. 512×320), then rerun the cell.
- **Black or noisy video on a T4**: set `FORCE_BF16 = True` in cell 3 and rerun cells 3 onward.
- **Session crashed while loading**: Colab ran out of system RAM. Restart the runtime (`Runtime` → `Restart session`) and run all again.
- **Slow or blurry motion**: use longer, more specific prompts and 40–50 steps.
"""


def main():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "accelerator": "GPU",
        "colab": {"gpuType": "T4", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    }
    nb.cells = [
        nbf.v4.new_markdown_cell(INTRO),
        nbf.v4.new_code_cell(GPU_CHECK),
        nbf.v4.new_code_cell(INSTALL),
        nbf.v4.new_code_cell(LOAD),
        nbf.v4.new_code_cell(HELPERS),
        nbf.v4.new_code_cell(T2V),
        nbf.v4.new_code_cell(I2V),
        nbf.v4.new_code_cell(SAVE),
        nbf.v4.new_markdown_cell(TIPS),
    ]
    out = Path(__file__).with_name("ltx_video_colab.ipynb")
    nbf.write(nb, out)
    print("Wrote", out)


if __name__ == "__main__":
    main()
