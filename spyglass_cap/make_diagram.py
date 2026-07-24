# Bemasste Querschnitts-Skizze des Halterings (Variante C).
s = 5.0
def sx(cx,x): return cx + x*s
def sy(by,z): return by - z*s
def poly(cx,by,pts,fill):
    d=" ".join(f"{sx(cx,x):.1f},{sy(by,z):.1f}" for x,z in pts)
    return f'<polygon points="{d}" fill="{fill}" stroke="#1a2b3c" stroke-width="1.6"/>'
def txt(x,y,t,anchor="middle",size=15,col="#1a2b3c",w="600"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Segoe UI,Arial" font-size="{size}" font-weight="{w}" fill="{col}">{t}</text>'
def dim(x1,y1,x2,y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c0392b" stroke-width="1.3" marker-start="url(#a)" marker-end="url(#a)"/>'

W,H=920,620
cx,by=460,470
hole_r,inner_r,outer_r=17.5,35.2,38.7
z0,z1,z2=0,20,23.5
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
o.append('<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,4 L8,1.5 L8,6.5 Z" fill="#c0392b"/></marker></defs>')
o.append(f'<rect width="{W}" height="{H}" fill="#f7f5f0"/>')
o.append(txt(W/2,42,"Haltering mit Guckloch – Querschnitt",size=23))
o.append(txt(W/2,66,"haelt die ausfahrbaren Teile im Rohr, in der Mitte frei zum Durchschauen",size=13,col="#6b7a89",w="400"))

# Rohr angedeutet (dashed), von unten in die Schuerze geschoben
tro,tri=35.0,32.5
for sgn in (-1,1):
    x=sx(cx,sgn*tri) if sgn<0 else sx(cx,tri)
    x0=sx(cx,sgn*35.0) if sgn<0 else sx(cx,tro)
    xa=min(sx(cx,sgn*tro),sx(cx,sgn*tri)); wdt=abs(sx(cx,tro)-sx(cx,tri))
    o.append(f'<rect x="{xa:.1f}" y="{sy(by,z1):.1f}" width="{wdt:.1f}" height="130" fill="#d9d2c4" stroke="#7f8c8d" stroke-width="1.2" stroke-dasharray="5 4"/>')
o.append(txt(cx,by+150,"Rohr (Ø70) – wird von unten reingeschoben",size=12,col="#7f8c8d",w="400"))

# Halbschnitte (rechts + gespiegelt links)
R=[(hole_r,z1),(hole_r,z2),(outer_r,z2),(outer_r,z0),(inner_r,z0),(inner_r,z1)]
L=[(-x,z) for x,z in R]
o.append(poly(cx,by,R,"#8fb8d8"))
o.append(poly(cx,by,L,"#8fb8d8"))

# Blickachse durch Guckloch
o.append(f'<line x1="{cx}" y1="{sy(by,z2)-70}" x2="{cx}" y2="{by+40}" stroke="#27ae60" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#a)"/>')
o.append(txt(cx,sy(by,z2)-78,"Blick",size=13,col="#27ae60"))

# Bemassung
o.append(dim(sx(cx,-hole_r),sy(by,z2)+22,sx(cx,hole_r),sy(by,z2)+22)); o.append(txt(cx,sy(by,z2)+16,"Guckloch Ø35",size=14,col="#c0392b"))
o.append(dim(sx(cx,-outer_r),by+30,sx(cx,outer_r),by+30)); o.append(txt(cx,by+50,"Ø 77 außen",size=14))
o.append(dim(sx(cx,-inner_r),by+8,sx(cx,inner_r),by+8)); o.append(txt(cx,by-4,"Ø 70,4 innen (Rohr Ø70 + Spiel)",size=12,col="#c0392b"))
o.append(dim(sx(cx,outer_r)+18,by,sx(cx,outer_r)+18,sy(by,z2))); o.append(txt(sx(cx,outer_r)+24,by-55,"23,5 mm",size=13,anchor="start"))
o.append(dim(sx(cx,outer_r)+18,by,sx(cx,outer_r)+18,sy(by,z1))); o.append(txt(sx(cx,outer_r)+24,by-48,"greift 20 mm",size=11,anchor="start",col="#6b7a89",w="400"))
# Halte-Nase markieren
o.append(txt(sx(cx,-26),sy(by,z1)-16,"Halte-Nase stoppt die Teile",size=11,col="#2c3e50",w="400",anchor="middle"))

o.append(txt(W/2,H-18,"Passung: 0,4 mm Spiel einkalkuliert. Zu stramm/locker? CLEARANCE im Skript ändern.",size=13,col="#6b7a89",w="400"))
o.append('</svg>')
open("/home/user/basic/spyglass_cap/haltering_skizze.svg","w").write("\n".join(o))
print("SVG geschrieben")
