#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1500,1020; S=2
AB="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
AR="/System/Library/Fonts/Supplemental/Arial.ttf"
AI="/System/Library/Fonts/Supplemental/Arial Italic.ttf"
def mono(sz):
    for p in ("/System/Library/Fonts/Menlo.ttc","/System/Library/Fonts/Supplemental/Courier New Bold.ttf"):
        try: return ImageFont.truetype(p,sz*S)
        except: pass
    return ImageFont.truetype(AB,sz*S)

WHITE="#F3F5F8"; MUTE="#9AA3AF"; DIM="#6B7280"
PANEL="#24272C"; CARD="#2B2F36"; BORD="#3A3F47"; BORD2="#454B54"; CODEBG="#16181C"
TEAL="#04A6A8"; CYAN="#24EDFF"; PINK="#FF3C84"; GREEN="#34D399"; INK="#08312F"
AWS="#FF9900"; AZ="#37A0E4"; GCP="#5B9BF5"

def build(cfg):
    img=Image.new("RGB",(W*S,H*S),"#1D2023")
    glow=Image.new("RGBA",(W*S,H*S),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([int(W*S*0.28),int(-H*S*0.38),int(W*S*0.92),int(H*S*0.38)],fill=(36,237,255,85))
    gd.ellipse([int(W*S*0.60),int(H*S*0.55),int(W*S*1.18),int(H*S*1.3)],fill=(255,60,132,70))
    gd.ellipse([int(W*S*0.0),int(H*S*0.35),int(W*S*0.45),int(H*S*1.0)],fill=(4,166,168,38))
    glow=glow.filter(ImageFilter.GaussianBlur(220*S//100))
    img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB")
    d=ImageDraw.Draw(img)
    def f(p,sz): return ImageFont.truetype(p,sz*S)
    def sc(b): return [b[0]*S,b[1]*S,b[2]*S,b[3]*S]
    def rr(b,r,fill=None,outline=None,width=1):
        d.rounded_rectangle(sc(b),radius=r*S,fill=fill,outline=outline,width=width*S)
    def T(x,y,t,font,fill,anchor="la"): d.text((x*S,y*S),t,font=font,fill=fill,anchor=anchor)
    def tw(t,font): return d.textlength(t,font=font)/S
    def dot(x,y,col,rad=4): d.ellipse([(x-rad)*S,(y-rad)*S,(x+rad)*S,(y+rad)*S],fill=col)
    def sparkle(cx,cy,r,col):
        pts=[(cx,cy-r),(cx+r*0.26,cy-r*0.26),(cx+r,cy),(cx+r*0.26,cy+r*0.26),
             (cx,cy+r),(cx-r*0.26,cy+r*0.26),(cx-r,cy),(cx-r*0.26,cy-r*0.26)]
        d.polygon([(x*S,y*S) for x,y in pts],fill=col)

    f_word=f(AB,27); f_tag=f(AR,17); f_sm=f(AR,12); f_smb=f(AB,12)
    f_lbl=f(AB,11); f_ask=f(AR,20); f_run=f(AB,14)
    f_big=f(AB,58); f_resl=f(AB,20); f_ress=f(AR,16)
    f_kn=f(AB,30); f_kl=f(AR,13); f_th=f(AB,12); f_td=f(AR,14); f_tdm=mono(13)

    # header
    rr((120,44,156,80),9,fill=TEAL); T(138,62,"C",f_word,"#FFFFFF",anchor="mm")
    T(168,62,"cloudaware",f_word,WHITE,anchor="lm")
    d.line([(372*S,50*S),(372*S,76*S)],fill=BORD2,width=2*S)
    T(390,54,cfg["tag1"],f_tag,WHITE); T(390,73,cfg["tag2"],f_sm,MUTE)
    # MCP chip top-right
    chip="MCP-native  ·  ask in plain English"; cwd=tw(chip,f_sm)
    cbx=1380-cwd-50
    rr((cbx,46,1380,80),17,outline=TEAL,width=1)
    sparkle(cbx+22,63,7,CYAN); T(cbx+36,63,chip,f_sm,WHITE,anchor="lm")

    # ---- ask / MCP hero card ----
    HX0,HY0,HX1,HY1=120,116,1380,398
    rr((HX0,HY0,HX1,HY1),18,fill=PANEL,outline=BORD,width=1)
    T(HX0+30,HY0+28,cfg["qlabel"],f_lbl,DIM,anchor="lm")
    # natural-language ask bar
    rr((HX0+30,HY0+44,HX1-30,HY0+96),10,fill=CODEBG,outline=BORD,width=1)
    sparkle(HX0+58,HY0+70,9,CYAN)
    T(HX0+80,HY0+70,cfg["ask"],f_ask,WHITE,anchor="lm")
    rr((HX1-120,HY0+54,HX1-44,HY0+86),8,fill=TEAL)
    T(HX1-82,HY0+70,"Ask",f_run,INK,anchor="mm")
    # channel tags — MCP highlighted
    cxp=HX0+30
    for t,hot in [("MCP",True),("REST API",False),("CLI",False)]:
        wd=tw(t,f_smb)+ (28 if not hot else 34)
        if hot:
            rr((cxp,HY0+112,cxp+wd,HY0+138),13,fill=TEAL)
            sparkle(cxp+15,HY0+125,5,INK); T(cxp+26,HY0+125,t,f_smb,INK,anchor="lm")
        else:
            rr((cxp,HY0+112,cxp+wd,HY0+138),13,outline=BORD2,width=1)
            T(cxp+14,HY0+125,t,f_smb,MUTE,anchor="lm")
        cxp+=wd+12
    d.line([(HX0+30)*S,(HY0+160)*S,(HX1-30)*S,(HY0+160)*S],fill=BORD,width=1*S)
    # result
    T(HX0+30,HY0+205,cfg["big"],f_big,CYAN,anchor="lm")
    bx=HX0+30+tw(cfg["big"],f_big)+28
    T(bx,HY0+188,cfg["resl"],f_resl,WHITE,anchor="lm")
    T(bx,HY0+216,cfg["ress"],f_ress,MUTE,anchor="lm")

    # ---- scale tiles ----
    tx0,tx1,ty0=120,1380,420; gap=18; n=len(cfg["tiles"]); cw=(tx1-tx0-gap*(n-1))/n; chh=132
    for i,(num,lab,acc) in enumerate(cfg["tiles"]):
        x=tx0+i*(cw+gap)
        rr((x,ty0,x+cw,ty0+chh),12,fill=CARD,outline=BORD,width=1)
        rr((x,ty0+18,x+4,ty0+chh-18),2,fill=acc)
        T(x+24,ty0+44,num,f_kn,WHITE,anchor="lm")
        T(x+24,ty0+82,lab,f_kl,MUTE,anchor="lm")

    # ---- result table ----
    BX0,BY0,BX1,BY1=120,574,1380,946
    rr((BX0,BY0,BX1,BY1),16,fill=PANEL,outline=BORD,width=1)
    sparkle(BX0+40,BY0+30,7,CYAN)
    T(BX0+56,BY0+28,cfg["tbl_title"],f_smb,WHITE,anchor="lm")
    T(BX1-30,BY0+28,cfg["tbl_sub"],f_sm,DIM,anchor="rm")
    cols=cfg["cols"]; hy=BY0+64
    for hdr,cx,_m in cols: T(cx,hy,hdr,f_th,DIM,anchor="lm")
    d.line([(BX0+28)*S,(hy+20)*S,(BX1-28)*S,(hy+20)*S],fill=BORD,width=1*S)
    ry=hy+52; rh=44
    for row in cfg["rows"]:
        for (hdr,cx,m),val in zip(cols,row["cells"]):
            if hdr=="PROVIDER":
                pcol={"AWS":AWS,"Azure":AZ,"GCP":GCP}[val]
                dot(cx+6,ry,pcol); T(cx+18,ry,val,f_td,WHITE,anchor="lm")
            else:
                T(cx,ry,val,(f_tdm if m else f_td),(WHITE if m else "#C7CDD6"),anchor="lm")
        d.line([(BX0+28)*S,(ry+rh-16)*S,(BX1-28)*S,(ry+rh-16)*S],fill="#2F343B",width=1*S)
        ry+=rh
    T(W/2,984,cfg["footer"],f_tag,MUTE,anchor="mm")

    final=img.resize((W,H),Image.LANCZOS); final.save(cfg["out"],"PNG"); print("saved",cfg["out"])

# ===================== AD A : single-cloud at scale (AWS) =====================
colsA=[("PUBLIC IP",150,True),("RESOURCE",380,True),("ACCOUNT",640,True),("REGION",900,False),("PROVIDER",1130,False)]
rowsA=[
 {"cells":["54.221.18.42","ec2  prod-web-01","aws  4471-2207","us-east-1","AWS"]},
 {"cells":["3.121.88.10","nat-gw-12","aws  9982-1043","eu-west-1","AWS"]},
 {"cells":["18.190.7.221","alb-edge-09","aws  1184-5566","us-west-2","AWS"]},
 {"cells":["52.14.33.7","ec2  batch-44","aws  7741-0098","us-east-2","AWS"]},
 {"cells":["35.171.2.155","eip  api-prod","aws  2207-3310","us-east-1","AWS"]},
 {"cells":["13.59.240.88","nlb-ingest-3","aws  6650-7782","us-west-1","AWS"]},
]
build({
 "out":"/Users/mmik/Documents/projects/reddit-ads/cloudaware_scale_aws_1500x1020.png",
 "tag1":"One AWS database","tag2":"ask once — answers across every account",
 "qlabel":"ASK ONCE  ·  5,127 AWS ACCOUNTS",
 "ask":"Show me every public IP address across all our AWS accounts",
 "big":"612","resl":"public IP addresses","ress":"across 5,127 AWS accounts  ·  answered in 1.9 s",
 "tiles":[("5,127","AWS accounts",AWS),("4.2M","Configuration items",AWS),
          ("3,000+","CI classes",CYAN),("18.6M","Relationships mapped",TEAL)],
 "tbl_title":"answer  ·  public IPs across every linked account","tbl_sub":"showing 6 of 612",
 "cols":colsA,"rows":rowsA,
 "footer":"Thousands of AWS accounts, one place to ask. Get answers across your whole estate — MCP, API, or CLI.",
})

# ===================== AD B : multi-cloud at scale =====================
colsB=[("PUBLIC IP",150,True),("RESOURCE",370,True),("SCOPE",600,True),("REGION",880,False),("PROVIDER",1120,False)]
rowsB=[
 {"cells":["54.221.18.42","ec2  prod-web-01","aws acct 4471","us-east-1","AWS"]},
 {"cells":["20.42.65.130","vm-app-07","azure sub  core","eastus","Azure"]},
 {"cells":["34.121.9.18","gce  gke-node-3","gcp proj  data","us-central1","GCP"]},
 {"cells":["3.121.88.10","nat-gw-12","aws acct 9982","eu-west-1","AWS"]},
 {"cells":["20.108.44.9","appgw-edge-2","azure sub  net","westeurope","Azure"]},
 {"cells":["35.190.12.77","lb-ingest-5","gcp proj  edge","europe-west1","GCP"]},
]
build({
 "out":"/Users/mmik/Documents/projects/reddit-ads/cloudaware_scale_multicloud_1500x1020.png",
 "tag1":"One multi-cloud database","tag2":"ask once — answers across AWS · Azure · GCP",
 "qlabel":"ASK ONCE  ·  AWS · AZURE · GCP",
 "ask":"List every public IP across all our AWS, Azure and GCP accounts",
 "big":"1,284","resl":"public IP addresses","ress":"across AWS, Azure & GCP  ·  one question  ·  2.3 s",
 "tiles":[("5,127","AWS accounts",AWS),("3,402","Azure subscriptions",AZ),
          ("1,860","GCP projects",GCP),("7.8M","Configuration items",CYAN)],
 "tbl_title":"answer  ·  public IPs unified across every cloud","tbl_sub":"showing 6 of 1,284",
 "cols":colsB,"rows":rowsB,
 "footer":"AWS, Azure and GCP in one inventory — ask once, get answers across every cloud. MCP, API, or CLI.",
})
