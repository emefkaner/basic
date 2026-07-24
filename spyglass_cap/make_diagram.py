# Erzeugt eine bemasste Querschnitts-Skizze beider Kappen als SVG.
s = 3.4
def sx(cx, x): return cx + x*s
def sy(by, z): return by - z*s
def poly(cx, by, pts, fill):
    d = " ".join(f"{sx(cx,x):.1f},{sy(by,z):.1f}" for x,z in pts)
    return f'<polygon points="{d}" fill="{fill}" stroke="#1a2b3c" stroke-width="1.5"/>'
def txt(x,y,t,anchor="middle",size=15,col="#1a2b3c",w="600"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Segoe UI,Arial" font-size="{size}" font-weight="{w}" fill="{col}">{t}</text>'
def dimline(x1,y1,x2,y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c0392b" stroke-width="1.2" marker-start="url(#a)" marker-end="url(#a)"/>'

W,H=940,560
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
out.append('<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,4 L8,1.5 L8,6.5 Z" fill="#c0392b"/></marker></defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#f7f5f0"/>')
out.append(txt(W/2,40,"Kappe fuer verkuerztes Piraten-Fernrohr  –  Querschnitte",size=22))

# ---- Variante A: Ueberstuelp ----
cx,by=250,430
oi,oo=35.2,38.2  # innen/aussen radius
A=[(-oo,0),(-oo,23),(oo,23),(oo,0),(oi,0),(oi,20),(-oi,20),(-oi,0)]
out.append(txt(cx,95,"A  Überstülp-Kappe",size=18,col="#2c3e50"))
out.append(txt(cx,118,"wenn 70 mm = Außen-Ø des Rohrs",size=13,col="#6b7a89",w="400"))
out.append(poly(cx,by,A,"#8fb8d8"))
# Rohr (angedeutet) schiebt sich von unten in die Oeffnung
out.append(f'<rect x="{sx(cx,-35):.1f}" y="{by:.1f}" width="{70*s:.1f}" height="55" fill="none" stroke="#7f8c8d" stroke-width="1.4" stroke-dasharray="5 4"/>')
out.append(txt(cx,by+78,"Rohr Ø70",size=12,col="#7f8c8d",w="400"))
out.append(dimline(sx(cx,-oo),by+18,sx(cx,oo),by+18)); out.append(txt(cx,by+38,"Ø 76,4 außen",size=13))
out.append(dimline(sx(cx,-oi),sy(by,20)+0,sx(cx,oi),sy(by,20)+0)); out.append(txt(cx,sy(by,20)-6,"Ø 70,4 innen (Rohr+Spiel)",size=12,col="#c0392b"))
out.append(dimline(sx(cx,oo)+16,by,sx(cx,oo)+16,sy(by,23))); out.append(txt(sx(cx,oo)+22,by-40,"23 mm",size=13,anchor="start"))
out.append(dimline(sx(cx,oo)+16,by,sx(cx,oo)+16,sy(by,20))); # skirt shown by same range approx

# ---- Variante B: Deckel+Zapfen ----
cx=690
pr,lr=12.3,35.0
B=[(-10.8,0),(-pr,1.5),(-pr,16),(-lr,16),(-lr,19),(lr,19),(lr,16),(pr,16),(pr,1.5),(10.8,0)]
out.append(txt(cx,95,"B  Deckel mit Zapfen",size=18,col="#2c3e50"))
out.append(txt(cx,118,"wenn 25 mm = mittige Öffnung/Bohrung",size=13,col="#6b7a89",w="400"))
out.append(poly(cx,by,B,"#c8a15a"))
# Rohrwand angedeutet, Zapfen steckt ins Loch
out.append(f'<rect x="{sx(cx,-13):.1f}" y="{by:.1f}" width="{26*s:.1f}" height="55" fill="none" stroke="#7f8c8d" stroke-width="1.4" stroke-dasharray="5 4"/>')
out.append(txt(cx,by+78,"Loch Ø25",size=12,col="#7f8c8d",w="400"))
out.append(dimline(sx(cx,-lr),sy(by,19)-14,sx(cx,lr),sy(by,19)-14)); out.append(txt(cx,sy(by,19)-20,"Ø 70 Deckel",size=13))
out.append(dimline(sx(cx,-pr),by+18,sx(cx,pr),by+18)); out.append(txt(cx,by+38,"Ø 24,6 Zapfen",size=13,col="#c0392b"))
out.append(dimline(sx(cx,lr)+16,by,sx(cx,lr)+16,sy(by,16))); out.append(txt(sx(cx,lr)+22,by-25,"Zapfen 16",size=12,anchor="start"))

out.append(txt(W/2,H-20,"Spiel/Passung: Standard 0,4 mm einkalkuliert  –  zu stramm/locker? CLEARANCE im Skript ändern",size=13,col="#6b7a89",w="400"))
out.append('</svg>')
open("/home/user/basic/spyglass_cap/kappen_skizze.svg","w").write("\n".join(out))
print("SVG geschrieben")
