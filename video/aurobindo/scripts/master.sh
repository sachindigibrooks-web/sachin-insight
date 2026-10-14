#!/bin/sh
# Bus glue compression, gain to -14.3 LUFS, brickwall limit at about -1.5 dBFS.
set -e
ffmpeg -v error -y -i out/mix_premaster.wav -af "acompressor=threshold=-14dB:ratio=2:attack=10:release=150" -c:a pcm_f32le out/mix_comp.wav
G=$(python3 -c "
import soundfile as sf, pyloudnorm as pyln
y,sr=sf.read('out/mix_comp.wav'); print(round(-14.3-pyln.Meter(sr).integrated_loudness(y),2))")
ffmpeg -v error -y -i out/mix_comp.wav -af "volume=${G}dB,alimiter=limit=0.84:attack=2:release=60:level=disabled" -c:a pcm_s24le out/mix_master.wav
ffmpeg -hide_banner -i out/mix_master.wav -af ebur128=peak=true -f null - 2>&1 | grep -E " I:|Peak:" | tail -2
