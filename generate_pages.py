#!/usr/bin/env python3
"""Génère des pages statiques pré-rendues par spot (SEO) à partir de data.json.

Chaque page /spots/<slug>/ est une mini-landing immersive : héros photo +
verdict géant, puis les conditions, avec les mêmes effets que l'app (halos
chauds, lumière au curseur, relief, parallaxe, pulsation, reveal).
Lancé après generate_data.py.
"""
import json
import os
import re
import unicodedata
from datetime import datetime, timezone

SITE_BASE = "https://loupeirrot.github.io/swelleo"   # ← deviendra https://swelleo.com
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "spots")


def clean_name(name: str) -> str:
    return re.sub(r"^[^\w(]+", "", name).strip()


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", clean_name(name).lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def verdict(score: float):
    if score >= 6.5:
        return ("GO", "#34e89e")
    if score >= 4.5:
        return ("OK", "#ffce6a")
    return ("FLAT", "#ff6b6b")


def mood_photo(score: float) -> str:
    if score >= 6.5:
        return "wave-epic"
    if score >= 4.5:
        return "wave-golden"
    return "wave-flat"


def best_window(hours):
    day = [h for h in hours if h.get("daytime")]
    pool = day or hours
    if not pool:
        return None
    return max(pool, key=lambda h: h.get("score", 0))


def fmt_hour(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return f"{dt.hour}h{dt.minute:02d}"
    except Exception:
        return ""


def next_tide(tides, region):
    ex = tides.get(region) or []
    now = datetime.now(timezone.utc)
    for e in ex:
        try:
            if datetime.fromisoformat(e["time"]) > now:
                t = "haute" if e["type"] == "haute" else "basse"
                return f"marée {t} à {fmt_hour(e['time'])}"
        except Exception:
            continue
    return ""


def esc(s: str) -> str:
    return (str(s or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#060d18">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{base}/assets/{photo}.webp">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{base}/assets/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@600,700&display=swap" rel="stylesheet">
<script type="application/ld+json">{jsonld}</script>
<style>
  :root{{--bg:#060d18;--bg2:#0a1626;--card:rgba(17,29,46,0.66);--stroke:rgba(255,255,255,0.10);
    --text:#eaf2f9;--dim:rgba(214,230,244,0.62);--go:#34e89e;
    --display:'Clash Display','Space Grotesk',sans-serif;--head:'Space Grotesk',sans-serif;
    --ease:cubic-bezier(.16,1,.3,1)}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:var(--head);color:var(--text);line-height:1.5;min-height:100dvh;font-variant-numeric:tabular-nums;
    -webkit-font-smoothing:antialiased;overflow-x:hidden;background:
      radial-gradient(60% 40% at 78% 6%,rgba(52,232,158,0.14),transparent 70%),
      radial-gradient(55% 45% at 12% 22%,rgba(44,196,182,0.12),transparent 70%),
      radial-gradient(48% 36% at 86% 50%,rgba(255,214,165,0.08),transparent 70%),
      radial-gradient(46% 34% at 6% 70%,rgba(255,205,150,0.06),transparent 70%),
      radial-gradient(80% 60% at 50% 110%,rgba(13,90,120,0.30),transparent 70%),
      linear-gradient(180deg,var(--bg),var(--bg2));background-attachment:fixed}}
  a{{color:var(--go);text-decoration:none}}
  .wrap{{max-width:680px;margin:0 auto;padding:16px 16px 60px;position:relative;z-index:1}}
  .top{{display:flex;align-items:center;gap:10px;padding:9px 4px 0}}
  .top img{{width:30px;height:30px;border-radius:8px}}
  .top b{{font-family:var(--head);font-size:1.05rem;font-weight:600}}
  .crumb{{font-size:0.82rem;color:var(--dim);margin:14px 4px 0}}

  .hero{{position:relative;min-height:clamp(380px,60vh,600px);border-radius:30px;overflow:hidden;margin-top:12px;
    display:flex;align-items:center;justify-content:center;isolation:isolate}}
  .hero-bg{{position:absolute;inset:0;z-index:-2;transform:translate3d(var(--hx,0),var(--hy,0),0) scale(1.06);transition:transform .2s ease-out}}
  .hero-bg img{{width:100%;height:100%;object-fit:cover;opacity:0.45}}
  .hero::before{{content:"";position:absolute;inset:0;z-index:-1;
    background:radial-gradient(70% 60% at 50% 36%,transparent,rgba(6,13,24,0.55) 78%),
      linear-gradient(180deg,rgba(6,13,24,0.35),rgba(6,13,24,0.10) 40%,rgba(6,13,24,0.85))}}
  .hero-inner{{text-align:center;padding:26px 18px}}
  .eyebrow{{display:inline-block;font-family:var(--head);font-size:0.66rem;letter-spacing:2.5px;text-transform:uppercase;
    color:var(--text);background:rgba(255,255,255,0.08);border:1px solid var(--stroke);padding:6px 13px;border-radius:999px;margin-bottom:16px}}
  .verdict{{font-family:var(--display);font-weight:700;font-size:clamp(4.5rem,26vw,10rem);line-height:0.84;letter-spacing:-0.02em;
    text-shadow:0 0 60px var(--glow,#34e89e);filter:saturate(1.1);transition:transform .2s ease-out;
    transform:translate3d(calc(var(--hx,0px) * -0.55),calc(var(--hy,0px) * -0.55),0);animation:verdictPulse 4.2s ease-in-out infinite}}
  .hero-sub{{font-family:var(--head);font-size:1.05rem;font-weight:600;margin-top:14px}}
  .hero-up{{font-size:0.86rem;color:var(--dim);margin-top:6px}}

  h1{{font-family:var(--head);font-size:1.35rem;font-weight:600;margin:26px 4px 4px}}
  .sub{{color:var(--dim);margin:0 4px 18px;font-size:0.95rem}}
  .glass{{background:
      radial-gradient(150% 130% at 76% -28%,rgba(255,227,188,0.26),rgba(255,227,188,0) 62%),
      radial-gradient(90% 70% at 18% 8%,rgba(255,236,205,0.10),transparent 55%),
      radial-gradient(120% 95% at 6% 120%,rgba(52,232,158,0.06),transparent 55%),
      rgba(17,29,46,0.66);
    border:1px solid var(--stroke);border-radius:22px;box-shadow:0 18px 50px rgba(2,8,18,0.5),inset 0 1px 0 rgba(255,255,255,0.14)}}
  .card{{position:relative;padding:20px;margin-bottom:16px;transform-style:preserve-3d}}
  .card::before{{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:3;
    background:radial-gradient(190px 190px at var(--mx,50%) var(--my,50%),rgba(255,248,230,0.32),rgba(255,248,230,0.06) 38%,transparent 60%);
    opacity:0;transition:opacity .3s var(--ease);mix-blend-mode:screen}}
  .card.lit::before{{opacity:1}}
  .card.lit{{transform:perspective(800px) rotateX(var(--ry,0deg)) rotateY(var(--rx,0deg)) scale(1.015);
    transition:transform .1s ease-out,box-shadow .3s var(--ease);z-index:5;
    box-shadow:0 34px 80px rgba(2,8,18,0.66),inset 0 1px 0 rgba(255,255,255,0.22)}}
  .rows{{display:grid;gap:8px}}
  .row{{display:flex;justify-content:space-between;gap:12px;font-size:0.96rem;border-top:1px solid var(--stroke);padding-top:9px}}
  .row:first-child{{border-top:0;padding-top:0}}
  .row span:first-child{{color:var(--dim)}}
  .actions{{display:flex;flex-wrap:wrap;gap:10px;margin:4px 0 8px}}
  .cta{{background:var(--go);color:#04231a;font-family:var(--head);font-weight:700;padding:13px 22px;border-radius:999px}}
  .btn2{{border:1px solid var(--stroke);padding:12px 18px;border-radius:999px;color:var(--text);background:var(--card)}}
  h2{{font-family:var(--head);font-size:1.05rem;font-weight:600;margin-bottom:10px}}
  .about{{color:var(--dim);font-size:0.95rem}}
  footer{{margin-top:30px;font-size:0.76rem;color:var(--dim);line-height:1.8;text-align:center}}

  .reveal{{opacity:0;transform:translateY(26px);filter:blur(8px);transition:opacity .8s var(--ease),transform .8s var(--ease),filter .8s ease}}
  .reveal.in{{opacity:1;transform:none;filter:none}}
  @keyframes verdictPulse{{0%,100%{{text-shadow:0 0 42px var(--glow,#34e89e)}}50%{{text-shadow:0 0 90px var(--glow,#34e89e),0 0 38px var(--glow,#34e89e)}}}}
  @media (hover:none){{.card::before{{display:none}}}}
  @media (prefers-reduced-motion:reduce){{
    .reveal{{opacity:1!important;transform:none!important;filter:none!important;transition:none}}
    .verdict,.hero-bg{{animation:none;transform:none}} .card.lit{{transform:none}}
  }}
</style>
<noscript><style>.reveal{{opacity:1;transform:none;filter:none}}</style></noscript>
</head>
<body>
<div class="wrap">
  <div class="top"><img src="{base}/assets/icon-192.png" alt="swelleo"><b>swelleo<span style="color:var(--go)">.</span></b></div>
  <div class="crumb"><a href="{base}/">Accueil</a> · {region}</div>

  <section id="hero" class="hero">
    <div class="hero-bg"><img src="{base}/assets/{photo}.webp" alt="Conditions de surf à {name}" fetchpriority="high"></div>
    <div class="hero-inner">
      <span class="eyebrow">{region} · {name}</span>
      <div class="verdict" style="--glow:{vcolor};color:{vcolor}">{vword}</div>
      <div class="hero-sub">{score}/10 · {when}</div>
      <div class="hero-up">{wave} · vent {wind}</div>
    </div>
  </section>

  <h1>Surf {name}</h1>
  <p class="sub">Prévision, houle, marée et webcam — le verdict go/no-go pour {name} ({region}).</p>

  <div class="card glass reveal">
    <div class="rows">
      <div class="row"><span>Houle</span><span>{wave}</span></div>
      <div class="row"><span>Vent</span><span>{wind} · {offshore}</span></div>
      {buoy_row}
      {tide_row}
    </div>
  </div>

  <div class="actions">
    <a class="cta" href="{base}/">Voir tous les spots →</a>
    {webcam_btn}
  </div>

  <div class="card glass reveal">
    <h2>À propos de ce spot</h2>
    <p class="about">Le verdict <strong style="color:{vcolor}">{vword}</strong> pour {name} est calculé à partir de la houle (hauteur, période, direction) et du vent, croisés avec l'orientation du spot. Ouvrez l'app pour le détail heure par heure et comparer avec les autres spots de {region}.</p>
  </div>

  <footer>
    Données houle &amp; vent : Open-Meteo · Bouées : Candhis / Cerema (Licence Ouverte) · Webcams : gosurf.fr &amp; partenaires.<br>
    Mis à jour le {updated}. swelleo — le verdict go/no-go pour savoir s'il faut aller surfer.
  </footer>
</div>
<script>
(function(){{
  var rev=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target);}}}});}},{{threshold:0.06}});
    rev.forEach(function(el){{io.observe(el);}});
  }} else {{ rev.forEach(function(el){{el.classList.add('in');}}); }}
  if(matchMedia('(hover:none)').matches||matchMedia('(prefers-reduced-motion:reduce)').matches)return;
  var cur=null,last=null,raf=0;
  function apply(){{
    raf=0;var e=last;if(!e)return;var card=e.target.closest?e.target.closest('.card'):null;
    if(cur&&cur!==card){{cur.classList.remove('lit');cur.style.removeProperty('--rx');cur.style.removeProperty('--ry');}}
    cur=card;if(!card)return;var r=card.getBoundingClientRect();var mx=(e.clientX-r.left)/r.width,my=(e.clientY-r.top)/r.height;
    card.style.setProperty('--mx',(mx*100).toFixed(1)+'%');card.style.setProperty('--my',(my*100).toFixed(1)+'%');
    card.style.setProperty('--rx',((mx-.5)*9).toFixed(2)+'deg');card.style.setProperty('--ry',(-(my-.5)*9).toFixed(2)+'deg');card.classList.add('lit');
    var hero=document.getElementById('hero'),hr=hero&&hero.getBoundingClientRect();
    if(hr&&e.clientY<hr.bottom&&e.clientY>hr.top){{hero.style.setProperty('--hx',(((e.clientX-hr.left)/hr.width-.5)*16).toFixed(1)+'px');hero.style.setProperty('--hy',(((e.clientY-hr.top)/hr.height-.5)*16).toFixed(1)+'px');}}
  }}
  addEventListener('pointermove',function(e){{last=e;if(!raf)raf=requestAnimationFrame(apply);}},{{passive:true}});
}})();
</script>
</body>
</html>
"""


def build():
    data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
    tides = data.get("tides", {})
    buoys = data.get("buoys", {})
    updated = datetime.now().strftime("%d/%m/%Y")
    os.makedirs(OUT_DIR, exist_ok=True)

    urls = [f"{SITE_BASE}/"]
    for spot in data["spots"]:
        name = clean_name(spot["name"])
        slug = slugify(spot["name"])
        region = spot["region"]
        w = best_window(spot.get("hours", []))
        if not w:
            continue
        score = w.get("score", 0)
        vword, vcolor = verdict(score)
        photo = mood_photo(score)
        wave = f"{w.get('wave_h','?')} m · {w.get('wave_p','?')} s · {w.get('swell_label','')}"
        wind = f"{w.get('wind_spd','?')} km/h {w.get('wind_label','')}"
        offshore = "offshore ✅" if w.get("offshore") else "onshore ⚠️"
        when = f"créneau ~{fmt_hour(w.get('time',''))}"

        b = buoys.get(region)
        buoy_row = ""
        if b and b.get("h") is not None:
            bl = f"{b['h']:.1f} m" + (f" · {round(b['period'])} s" if b.get("period") else "") + (f" · {round(b['temp'])}°C" if b.get("temp") is not None else "")
            buoy_row = f'<div class="row"><span>Bouée live ({esc(b.get("name") or b.get("code",""))})</span><span>{bl}</span></div>'
        tide = next_tide(tides, region)
        tide_row = f'<div class="row"><span>Marée</span><span>{esc(tide)}</span></div>' if tide else ""

        webcam_btn = f'<a class="btn2" href="{esc(spot["webcam"])}" target="_blank" rel="noopener">📹 Webcam live</a>' if spot.get("webcam") else ""

        url = f"{SITE_BASE}/spots/{slug}/"
        title = f"Surf {name} — prévision & conditions | swelleo"
        desc = f"Verdict {vword} pour {name} ({region}) : {wave}, vent {wind}. Prévision, marée et webcam en direct sur swelleo."
        jsonld = json.dumps({
            "@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": url,
            "about": {"@type": "Place", "name": name,
                      "geo": {"@type": "GeoCoordinates", "latitude": spot.get("lat"), "longitude": spot.get("lon")}},
        }, ensure_ascii=False)

        html = PAGE.format(
            title=esc(title), desc=esc(desc), url=url, base=SITE_BASE, region=esc(region), name=esc(name),
            vword=vword, vcolor=vcolor, score=score, when=esc(when), wave=esc(wave), wind=esc(wind),
            offshore=offshore, photo=photo, buoy_row=buoy_row, tide_row=tide_row, webcam_btn=webcam_btn,
            updated=updated, jsonld=jsonld,
        )
        os.makedirs(os.path.join(OUT_DIR, slug), exist_ok=True)
        with open(os.path.join(OUT_DIR, slug, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        urls.append(url)

    today = datetime.now().strftime("%Y-%m-%d")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
    sm.append("</urlset>")
    with open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))

    with open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE}/sitemap.xml\n")

    print(f"✅ {len(urls)-1} pages spot générées + sitemap.xml + robots.txt")


if __name__ == "__main__":
    build()
