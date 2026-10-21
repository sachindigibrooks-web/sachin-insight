import asyncio, json, sys, os, ssl, edge_tts, edge_tts.communicate as ec
ec._SSL_CTX=ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
d=os.path.dirname(os.path.abspath(__file__))
lines=json.load(open(f"{d}/lines.json"))
async def one(l):
    c=edge_tts.Communicate(l["tts"], l.get("voice","hi-IN-MadhurNeural"), rate=l.get("rate","+8%"), pitch=l.get("pitch","-6Hz"), boundary="WordBoundary")
    words=[]
    with open(f"{d}/{l['id']}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": words.append([ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7,ch["text"]])
    json.dump(words,open(f"{d}/{l['id']}.words.json","w"),ensure_ascii=False)
async def main():
    for l in lines: await one(l)
asyncio.run(main())
