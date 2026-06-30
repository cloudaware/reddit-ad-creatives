#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1500,1020; S=2
AB="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
AR="/System/Library/Fonts/Supplemental/Arial.ttf"
def mono(sz):
    for p in ("/System/Library/Fonts/Menlo.ttc","/System/Library/Fonts/Supplemental/Courier New Bold.ttf"):
        try: return ImageFont.truetype(p,sz*S)
        except: pass
    return ImageFont.truetype(AB,sz*S)

# LIGHT palette
BG="#F5F7FA"; WHITE="#FFFFFF"
INKT="#16202B"; MUTE="#5A6678"; DIM="#8A94A6"
CARD="#FFFFFF"; BORD="#E3E7EE"; BORD2="#D5DAE3"; CODEBG="#F1F4F8"
TEAL="#04A6A8"; TEALD="#03898B"; CYAN="#0FB5C9"; PINK="#FF3C84"; GREEN="#1F9D5B"
AWS="#FF9900"; AZ="#1F8FE5"; GCP="#2FA85A"

def build(cfg):
    base=Image.new("RGB",(W*S,H*S),BG)
    # subtle brand tint glows on white
    glow=Image.new("RGBA",(W*S,H*S),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([int(W*S*0.45),int(-H*S*0.30),int(W*S*1.05),int(H*S*0.30)],fill=(15,181,201,26))
    gd.ellipse([int(-W*S*0.15),int(H*S*0.55),int(W*S*0.40),int(H*S*1.25)],fill=(255,60,132,16))
    glow=glow.filter(ImageFilter.GaussianBlur(240*S//100))
    base=Image.alpha_composite(base.convert("RGBA"),glow)

    # ---- card boxes (for shadow pre-pass) ----
    HX0,HY0,HX1,HY1=120,116,1380,398
    tx0,tx1,ty0=120,1380,420; tgap=18; nT=len(cfg["tiles"]); tw_=(tx1-tx0-tgap*(nT-1))/nT; chh=132
    tiles_box=[(tx0+i*(tw_+tgap),ty0,tx0+i*(tw_+tgap)+tw_,ty0+chh) for i in range(nT)]
    BX0,BY0,BX1,BY1=120,574,1380,946
    boxes=[(HX0,HY0,HX1,HY1)]+tiles_box+[(BX0,BY0,BX1,BY1)]
    # shadow layer
    sh=Image.new("RGBA",(W*S,H*S),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    for b in boxes:
        sd.rounded_rectangle([b[0]*S,(b[1]+10)*S,b[2]*S,(b[3]+14)*S],radius=16*S,fill=(20,30,50,40))
    sh=sh.filter(ImageFilter.GaussianBlur(16*S//1))
    base=Image.alpha_composite(base,sh)
    img=base.convert("RGB"); d=ImageDraw.Draw(img)

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
    T(168,62,"cloudaware",f_word,INKT,anchor="lm")
    d.line([(372*S,50*S),(372*S,76*S)],fill=BORD2,width=2*S)
    T(390,54,cfg["tag1"],f_tag,INKT); T(390,73,cfg["tag2"],f_sm,MUTE)
    chip="MCP-native  ·  ask in plain English"; cwd=tw(chip,f_sm)
    cbx=1380-cwd-50
    rr((cbx,46,1380,80),17,fill="#E9FAFB",outline=TEAL,width=1)
    sparkle(cbx+22,63,7,TEAL); T(cbx+36,63,chip,f_sm,TEALD,anchor="lm")

    # ---- ask / MCP hero card ----
    rr((HX0,HY0,HX1,HY1),18,fill=CARD,outline=BORD,width=1)
    T(HX0+30,HY0+28,cfg["qlabel"],f_lbl,DIM,anchor="lm")
    rr((HX0+30,HY0+44,HX1-30,HY0+96),10,fill=CODEBG,outline=BORD,width=1)
    sparkle(HX0+58,HY0+70,9,TEAL)
    T(HX0+80,HY0+70,cfg["ask"],f_ask,INKT,anchor="lm")
    rr((HX1-120,HY0+54,HX1-44,HY0+86),8,fill=TEAL)
    T(HX1-82,HY0+70,"Ask",f_run,"#FFFFFF",anchor="mm")
    cxp=HX0+30
    for t,hot in [("MCP",True),("REST API",False),("CLI",False)]:
        wd=tw(t,f_smb)+ (28 if not hot else 34)
        if hot:
            rr((cxp,HY0+112,cxp+wd,HY0+138),13,fill=TEAL)
            sparkle(cxp+15,HY0+125,5,"#FFFFFF"); T(cxp+26,HY0+125,t,f_smb,"#FFFFFF",anchor="lm")
        else:
            rr((cxp,HY0+112,cxp+wd,HY0+138),13,outline=BORD2,width=1)
            T(cxp+14,HY0+125,t,f_smb,MUTE,anchor="lm")
        cxp+=wd+12
    d.line([(HX0+30)*S,(HY0+160)*S,(HX1-30)*S,(HY0+160)*S],fill=BORD,width=1*S)
    T(HX0+30,HY0+205,cfg["big"],f_big,TEAL,anchor="lm")
    bx=HX0+30+tw(cfg["big"],f_big)+28
    T(bx,HY0+188,cfg["resl"],f_resl,INKT,anchor="lm")
    T(bx,HY0+216,cfg["ress"],f_ress,MUTE,anchor="lm")

    # ---- scale tiles ----
    for i,(num,lab,acc) in enumerate(cfg["tiles"]):
        b=tiles_box[i]; x=b[0]
        rr(b,12,fill=CARD,outline=BORD,width=1)
        rr((x,ty0+18,x+4,ty0+chh-18),2,fill=acc)
        T(x+24,ty0+44,num,f_kn,INKT,anchor="lm")
        T(x+24,ty0+82,lab,f_kl,MUTE,anchor="lm")

    # ---- result table ----
    rr((BX0,BY0,BX1,BY1),16,fill=CARD,outline=BORD,width=1)
    sparkle(BX0+40,BY0+30,7,TEAL)
    T(BX0+56,BY0+28,cfg["tbl_title"],f_smb,INKT,anchor="lm")
    T(BX1-30,BY0+28,cfg["tbl_sub"],f_sm,DIM,anchor="rm")
    cols=cfg["cols"]; hy=BY0+64
    for hdr,cx,_m in cols: T(cx,hy,hdr,f_th,DIM,anchor="lm")
    d.line([(BX0+28)*S,(hy+20)*S,(BX1-28)*S,(hy+20)*S],fill=BORD,width=1*S)
    ry=hy+52; rh=44
    for row in cfg["rows"]:
        for (hdr,cx,m),val in zip(cols,row["cells"]):
            if hdr=="PROVIDER":
                pcol={"AWS":AWS,"Azure":AZ,"GCP":GCP}[val]
                dot(cx+6,ry,pcol); T(cx+18,ry,val,f_td,INKT,anchor="lm")
            else:
                T(cx,ry,val,(f_tdm if m else f_td),(INKT if m else "#49505E"),anchor="lm")
        d.line([(BX0+28)*S,(ry+rh-16)*S,(BX1-28)*S,(ry+rh-16)*S],fill="#EEF1F5",width=1*S)
        ry+=rh
    T(W/2,984,cfg["footer"],f_tag,MUTE,anchor="mm")

    final=img.resize((W,H),Image.LANCZOS); final.save(cfg["out"],"PNG"); print("saved",cfg["out"])

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
 "out":"/Users/mmik/Documents/projects/reddit-ads/cloudaware_scale_aws_light_1500x1020.png",
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
 "out":"/Users/mmik/Documents/projects/reddit-ads/cloudaware_scale_multicloud_light_1500x1020.png",
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
