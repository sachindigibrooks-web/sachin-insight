import json, subprocess, os, sys
d=os.path.dirname(os.path.abspath(__file__))
lines=json.load(open(f"{d}/lines.json"))
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
t=0.25; tl=[]; parts=[]
for l in lines:
    w=json.load(open(f"{d}/{l['id']}.words.json"))
    end=w[-1][1]+0.08
    wav=f"{d}/{l['id']}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"{d}/{l['id']}.mp3","-t",str(end),"-ar","48000","-ac","1",wav],check=True)
    caps=l["cap"].split()
    if len(caps)==len(w): cw=[[t+a,t+b,c] for (a,b,_),c in zip(w,caps)]
    else:
        s0,s1=w[0][0],w[-1][1]; tot=sum(len(c)+2 for c in caps); acc=s0; cw=[]
        for c in caps:
            dd=(s1-s0)*(len(c)+2)/tot; cw.append([t+acc,t+acc+dd,c]); acc+=dd
    tl.append({"id":l["id"],"start":t,"end":t+end,"words":cw,"cap":l["cap"]})
    parts.append((wav,t)); t+=end+l["gap"]
total=t+0.3
inputs=[];filt=[]
for i,(p,st) in enumerate(parts):
    inputs+=["-i",p]; filt.append(f"[{i}]adelay={int(st*1000)}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(parts)))+f"amix=inputs={len(parts)}:normalize=0,apad,atrim=0:{total}[o]")
subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(filt),"-map","[o]","-ar","48000",f"{d}/vo.wav"],check=True)
json.dump({"total":total,"lines":tl},open(f"{d}/timeline.json","w"),ensure_ascii=False,indent=1)
for x in tl: print(f"{x['id']:4} {x['start']:6.2f}-{x['end']:6.2f}  {x['cap']}")
print("TOTAL",total)
