import html, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from month import HG, PF

W, H = 1200, 900

BRANDS = {
"hg": dict(
  fonts="https://fonts.googleapis.com/css2?family=Metrophobic&family=Roboto:wght@400;500;700;900&display=block",
  css="""
  :root{--p:#004D71;--d:#2C353D;--a:#38C6F4;--a2:#75CDD7;--l:#ABDFEA;--w:#FFFFFF;--onA:#00324a;
        --hf:'Metrophobic',sans-serif;--bf:'Roboto',sans-serif;--hw:400;--ls:-0.5px}
  """,
  logo="img/hg_logo_t.png", logo_on_dark="chip", motif="glass",
),
"pf": dict(
  fonts="https://fonts.googleapis.com/css2?family=Rubik:wght@500;700;800;900&family=Roboto:wght@400;500;700&display=block",
  css="""
  :root{--p:#000000;--d:#111111;--a:#DEE101;--a2:#DEE101;--l:#F4F4F4;--w:#FFFFFF;--onA:#000000;
        --hf:'Rubik',sans-serif;--bf:'Roboto',sans-serif;--hw:800;--ls:-1px}
  """,
  logo="img/pf_logo_nophone.png", logo_on_dark="chip", motif="picket",
),
}

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#777;display:flex;flex-wrap:wrap;gap:30px;padding:30px}
.ab{position:relative;width:1200px;height:900px;overflow:hidden;background:var(--d);font-family:var(--bf);color:var(--w)}
.ph{position:absolute;background-size:cover;background-repeat:no-repeat}
.h{font-family:var(--hf);font-weight:var(--hw);letter-spacing:var(--ls);line-height:1.08;text-wrap:balance}
.nw{white-space:nowrap}
.vbox{position:absolute;display:flex;flex-direction:column;justify-content:center;z-index:10}
.h em{font-style:normal;color:var(--a)}
.tag{display:inline-flex;align-items:center;gap:10px;font:700 21px/1 var(--bf);letter-spacing:3px;text-transform:uppercase;color:var(--a)}
.tag:before{content:"";width:34px;height:3px;background:var(--a)}
.sub{font:400 27px/1.32 var(--bf);color:rgba(255,255,255,.9)}
.chip{display:inline-flex;align-items:center;gap:12px;background:var(--a);color:var(--onA);font:700 22px/1 var(--bf);padding:18px 30px;border-radius:999px;letter-spacing:.3px}
.chip:after{content:"";width:12px;height:12px;border-top:3px solid var(--onA);border-right:3px solid var(--onA);transform:rotate(45deg);margin-left:4px}
.logo{position:absolute;z-index:20}
.logo img{display:block;height:100%;width:auto}
.logo.chipbg{background:#fff;border-radius:18px;padding:12px 18px;box-shadow:0 8px 30px rgba(0,0,0,.25)}
.shade-b{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 35%,rgba(0,0,0,.78) 100%)}
.shade-l{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.78) 0%,rgba(0,0,0,.25) 60%,rgba(0,0,0,0) 100%)}
.motif{position:absolute;pointer-events:none;z-index:5}
.lbl{position:absolute;font:700 20px/1 var(--bf);letter-spacing:2px;text-transform:uppercase;background:var(--a);color:var(--onA);padding:12px 18px;border-radius:8px;z-index:6}
"""

def head_html(s):
    s = html.escape(s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"(\w+(?:-\w+)+)", r'<span class="nw">\1</span>', s)
    return s.replace("|", "<br>")

def ph(src, focus, style):
    return f'<div class="ph" style="background-image:url(ph_{SITE}/{src});background-position:{focus};{style}"></div>'

def logo(b, x, y, h, dark=True, right=False):
    h = int(h * (1.3 if SITE == "hg" else 0.95))
    pos = f"right:{x}px" if right else f"left:{x}px"
    if b["logo_on_dark"] == "chip" and dark:
        return f'<div class="logo chipbg" style="{pos};top:{y}px;height:{h+24}px"><img src="{b["logo"]}"></div>'
    return f'<div class="logo" style="{pos};top:{y}px;height:{h}px"><img src="{b["logo"]}"></div>'

def motif(b, kind, style=""):
    if b["motif"] == "glass":
        # two translucent slanted panes, echoing the logo mark
        if kind == "corner":
            return (f'<svg class="motif" style="{style}" width="260" height="300" viewBox="0 0 260 300">'
                    '<polygon points="60,40 200,0 200,250 60,290" fill="#38C6F4" opacity=".55"/>'
                    '<polygon points="110,60 250,20 250,270 110,300" fill="#75CDD7" opacity=".45"/></svg>')
        return (f'<svg class="motif" style="{style}" width="420" height="900" viewBox="0 0 420 900">'
                '<polygon points="120,0 300,0 180,900 0,900" fill="#38C6F4" opacity=".10"/>'
                '<polygon points="260,0 420,0 300,900 140,900" fill="#75CDD7" opacity=".08"/></svg>')
    # picket fence silhouette
    n = 9 if kind == "corner" else 24
    w = 26
    pts = "".join(f'<polygon points="{i*40},{60} {i*40+w/2},{30} {i*40+w},{60} {i*40+w},{140} {i*40},{140}" fill="#DEE101"/>' for i in range(n))
    rail = f'<rect x="0" y="78" width="{n*40}" height="10" fill="#DEE101"/><rect x="0" y="112" width="{n*40}" height="10" fill="#DEE101"/>'
    return f'<svg class="motif" style="{style}" width="{n*40}" height="140" viewBox="0 0 {n*40} 140">{pts}{rail}</svg>'

def text_block(p, hsize, width, sub=True, chip=True, tag=True):
    out = f'<div style="width:{width}px">'
    if tag and p["tag"]:
        out += f'<div class="tag" style="margin-bottom:26px">{html.escape(p["tag"])}</div>'
    out += f'<div class="h" style="font-size:{hsize}px">{head_html(p["head"])}</div>'
    if sub and p.get("sub"):
        out += f'<div class="sub" style="margin-top:24px">{html.escape(p["sub"])}</div>'
    if chip and p.get("chip"):
        out += f'<div style="margin-top:34px"><span class="chip">{html.escape(p["chip"])}</span></div>'
    return out + "</div>"

def vbox(left, top, bottom, width, inner):
    return f'<div class="vbox" style="left:{left}px;top:{top}px;bottom:{bottom}px;width:{width}px">{inner}</div>'

def T_split(p, b):
    return (ph(p["photos"][0], p["focus"], "left:0;top:0;width:640px;height:900px")
            + f'<div style="position:absolute;left:640px;top:0;width:560px;height:900px;background:var(--p)"></div>'
            + (motif(b, "band", "left:780px;top:0") if b["motif"]=="glass" else motif(b, "corner", "left:840px;bottom:0"))
            + logo(b, 700, 60, 96)
            + vbox(700, 220, 60, 450, text_block(p, 58, 450)))

def T_offer(p, b):
    return (ph(p["photos"][0], p["focus"], "inset:0")
            + '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.82),rgba(0,0,0,.35))"></div>'
            + logo(b, 60, 56, 92)
            + f'<div style="position:absolute;left:60px;top:230px;width:660px;padding:44px 46px 48px;background:var(--a);color:var(--onA);border-radius:28px;box-shadow:0 30px 60px rgba(0,0,0,.35);z-index:10">'
            + f'<div style="font:800 21px/1 var(--bf);letter-spacing:3px;text-transform:uppercase;margin-bottom:22px;opacity:.85">{html.escape(p["tag"])}</div>'
            + f'<div class="h" style="font-size:68px;line-height:1.22;color:var(--onA)">{head_html(p["head"]).replace("<em>","<em style=\"display:inline-block;line-height:1.08;color:var(--w);background:var(--p);padding:2px 16px 8px;margin:4px 0;border-radius:10px\">")}</div>'
            + f'<div style="font:500 27px/1.3 var(--bf);margin-top:22px">{html.escape(p["sub"])}</div>'
            + f'<div style="margin-top:30px"><span class="chip" style="background:var(--p);color:var(--w)">{html.escape(p["chip"])}</span></div></div>'
            + motif(b, "corner", "right:40px;bottom:30px" if b["motif"]=="glass" else "right:0;bottom:0"))

def T_faq(p, b):
    return (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
            + f'<div style="position:absolute;left:30px;top:-150px;font:900 820px/1 var(--hf);color:var(--a);opacity:.09">?</div>'
            + ph(p["photos"][0], p["focus"], "right:56px;top:56px;width:470px;height:788px;border-radius:26px;box-shadow:0 20px 50px rgba(0,0,0,.35)")
            + logo(b, 64, 60, 84)
            + vbox(64, 210, 60, 560,
                   f'<div><div class="tag" style="margin-bottom:26px">{html.escape(p["tag"])}</div>'
                   + f'<div class="h" style="font-size:62px">{head_html(p["head"])}</div>'
                   + f'<div style="margin-top:28px;padding-left:22px;border-left:4px solid var(--a)" class="sub">{html.escape(p["sub"])}</div>'
                   + f'<div style="margin-top:36px"><span class="chip">{html.escape(p["chip"])}</span></div></div>'))

PIN = '<svg width="22" height="28" viewBox="0 0 24 30"><path d="M12 0C5.4 0 0 5.3 0 11.9 0 20.8 12 30 12 30s12-9.2 12-18.1C24 5.3 18.6 0 12 0zm0 16.5a4.6 4.6 0 1 1 0-9.2 4.6 4.6 0 0 1 0 9.2z" fill="currentColor"/></svg>'

def T_local(p, b):
    return (ph(p["photos"][0], p["focus"], "inset:0")
            + '<div class="shade-b" style="background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,.15) 50%,rgba(0,0,0,.85) 100%)"></div>'
            + f'<div style="position:absolute;left:60px;top:60px;display:flex;align-items:center;gap:12px;background:var(--a);color:var(--onA);font:700 24px/1 var(--bf);padding:16px 26px;border-radius:999px;z-index:10">{PIN}{html.escape(p["tag"])}</div>'
            + logo(b, 60, 46, 92, right=True)
            + f'<div style="position:absolute;left:60px;bottom:64px;z-index:10">{text_block(p,82,900,tag=False)}</div>')

def T_glass(p, b):
    return (ph(p["photos"][0], p["focus"], "inset:0")
            + '<div style="position:absolute;inset:0;background:linear-gradient(0deg,rgba(0,0,0,.35),rgba(0,0,0,0) 60%)"></div>'
            + logo(b, 56, 52, 88)
            + f'<div style="position:absolute;left:56px;bottom:56px;width:640px;padding:44px;border-radius:28px;background:rgba(10,20,28,.55);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1.5px solid rgba(255,255,255,.28);z-index:10">'
            + text_block(p, 60, 552) + "</div>"
            + motif(b, "corner", "right:30px;bottom:30px;opacity:.55" if b["motif"]=="glass" else "right:0;bottom:0;opacity:.95"))

def T_trio(p, b):
    out = (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
           + logo(b, 56, 44, 80)
           + f'<div style="position:absolute;left:56px;top:205px;z-index:10">{text_block(p,58,760,sub=False,chip=False)}</div>')
    for i, (src, lab) in enumerate(zip(p["photos"], p["labels"])):
        x = 56 + i * 370
        out += ph(src, p["focus"], f"left:{x}px;top:450px;width:348px;height:400px;border-radius:20px")
        out += f'<div class="lbl" style="left:{x+18}px;top:{450+400-62}px">{html.escape(lab)}</div>'
    out += f'<div style="position:absolute;right:56px;top:330px;z-index:10"><span class="chip">{html.escape(p["chip"])}</span></div>'
    return out

def T_diagonal(p, b):
    return (ph(p["photos"][0], p["focus"], "inset:0")
            + f'<div style="position:absolute;inset:0;background:var(--p);clip-path:polygon(0 0,62% 0,46% 100%,0 100%);opacity:.96"></div>'
            + f'<div style="position:absolute;inset:0;background:var(--a);clip-path:polygon(62% 0,64.5% 0,48.5% 100%,46% 100%)"></div>'
            + logo(b, 60, 56, 90)
            + vbox(60, 210, 60, 480, text_block(p, 64, 480)))

def T_frame(p, b):
    return (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
            + ph(p["photos"][0], p["focus"], "left:40px;top:40px;width:1120px;height:540px;border-radius:22px")
            + logo(b, 70, 66, 84)
            + f'<div style="position:absolute;left:70px;top:620px;width:720px;z-index:10">'
            + f'<div class="tag" style="margin-bottom:18px">{html.escape(p["tag"])}</div>'
            + f'<div class="h" style="font-size:56px">{head_html(p["head"]).replace("<br>"," ")}</div>'
            + f'<div class="sub" style="margin-top:14px;font-size:25px">{html.escape(p["sub"])}</div></div>'
            + f'<div style="position:absolute;right:70px;top:700px;z-index:10"><span class="chip">{html.escape(p["chip"])}</span></div>')

def T_thanks(p, b):
    return (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
            + ((motif(b, "band", "left:0;top:0;opacity:.9") + motif(b, "band", "right:0;top:0;transform:scaleX(-1);opacity:.9")) if b["motif"]=="glass" else "")
            + (motif(b, "wide", "left:0;bottom:-10px;opacity:.25") if b["motif"]=="picket" else "")
            + ph(p["photos"][0], p["focus"], "left:620px;top:120px;width:500px;height:660px;border-radius:250px 250px 26px 26px;box-shadow:0 20px 50px rgba(0,0,0,.35);border:6px solid var(--a)")
            + logo(b, 80, 80, 90)
            + vbox(80, 220, 120, 500, text_block(p, 74, 500, chip=False)))

def T_beforeafter(p, b):
    labels = p.get("labels", ["Before", "After"])
    return (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
            + ph(p["photos"][0], p["focus"], "left:0;top:0;width:598px;height:650px")
            + ph(p["photos"][1], p["focus"], "left:602px;top:0;width:598px;height:650px")
            + f'<div class="lbl" style="left:30px;top:30px;background:#fff;color:#111">{labels[0]}</div>'
            + f'<div class="lbl" style="left:632px;top:30px">{labels[1]}</div>'
            + f'<div style="position:absolute;left:592px;top:0;width:16px;height:650px;background:var(--a)"></div>'
            + logo(b, 60, 712, 80)
            + f'<div style="position:absolute;left:330px;top:690px;width:520px;z-index:10">'
            + f'<div class="tag" style="margin-bottom:14px">{html.escape(p["tag"])}</div>'
            + f'<div class="h" style="font-size:46px">{head_html(p["head"])}</div>'
            + (f'<div class="sub" style="margin-top:10px;font-size:23px">{html.escape(p["sub"])}</div>' if p.get("sub") else "") + "</div>"
            + f'<div style="position:absolute;right:56px;top:752px;z-index:10"><span class="chip">{html.escape(p["chip"])}</span></div>')

def T_spotlight(p, b):
    a, c, d = p["photos"]
    return (f'<div style="position:absolute;inset:0;background:var(--p)"></div>'
            + ph(a, p["focus"], "left:560px;top:40px;width:600px;height:500px;border-radius:22px")
            + ph(c, p["focus"], "left:560px;top:560px;width:290px;height:300px;border-radius:22px")
            + ph(d, p["focus"], "left:870px;top:560px;width:290px;height:300px;border-radius:22px")
            + logo(b, 60, 60, 88)
            + vbox(60, 210, 60, 460, text_block(p, 68, 460)))

TPL = dict(split=T_split, offer=T_offer, faq=T_faq, local=T_local, glass=T_glass, trio=T_trio,
           diagonal=T_diagonal, frame=T_frame, thanks=T_thanks, beforeafter=T_beforeafter, spotlight=T_spotlight)

FIT = """<script>
document.fonts.ready.then(()=>{
  document.querySelectorAll('.h').forEach(h=>{
    let fs=parseFloat(getComputedStyle(h).fontSize);
    const box=h.closest('.vbox');
    const bad=()=>h.scrollWidth>h.clientWidth+1||(box&&box.scrollHeight>box.clientHeight+1);
    while(bad()&&fs>30){fs-=2;h.style.fontSize=fs+'px';}
  });
  document.body.dataset.fit='1';
});
</script>"""

def build(site, posts):
    global SITE
    SITE = site
    b = BRANDS[site]
    arts = []
    for i, p in enumerate(posts, 1):
        arts.append(f'<div class="ab" id="{site}_{i:02d}">{TPL[p["tpl"]](p, b)}</div>')
    doc = (f'<!doctype html><html><head><meta charset="utf-8"><link href="{b["fonts"]}" rel="stylesheet">'
           f'<style>{b["css"]}{BASE_CSS}</style></head><body>{"".join(arts)}{FIT}</body></html>')
    open(os.path.join(os.path.dirname(__file__), f"banners_{site}.html"), "w").write(doc)

if __name__ == "__main__":
    build("hg", HG); build("pf", PF); print("ok")
