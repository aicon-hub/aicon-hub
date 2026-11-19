"""Original AiCoN SVG cards. Self-contained images, no scripts or remote resources."""
from pathlib import Path
import json,base64,re,os,html
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cards'
STATIC=os.environ.get('STATIC')=='1'
FONT=''.join("@font-face{font-family:Outfit;font-style:normal;font-weight:"+w+";src:url(data:font/woff;base64,"+base64.b64encode((OUT/f'fonts/outfit-{w}.woff').read_bytes()).decode()+") format('woff')}" for w in ['400','600','700'])
THEMES={'light':{'bg':'#faf9f6','panel':'#ffffff','ink':'#1c2425','muted':'#62675f','rule':'#e0e2da','soft':'#efece3','sage':'#d6e4c5'},'dark':{'bg':'#111411','panel':'#1a1e19','ink':'#f5f5ed','muted':'#b4bcae','rule':'#343c30','soft':'#242c22','sage':'#c3d9aa'}}
ORANGE='#ff682f'
def text(x,y,value,size=24,weight=400,fill=None,extra=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '+(f'fill="{fill}" 'if fill else '')+f'{extra}>{html.escape(str(value))}</text>'
def wrap(value,maxchars):
 out=[];line=''
 for w in value.split():
  if len(line+' '+w)>maxchars:out.append(line);line=w
  else:line=(line+' '+w).strip()
 if line:out.append(line)
 return out

def svg(kind,theme,mobile,s):
 c=THEMES[theme];w=420 if mobile else 840;pad=24 if mobile else 36
 heights={'hero':440 if mobile else 365,'activity':310 if mobile else 260,'calendar':325 if mobile else 280,'guides':160 if mobile else 145,'community':160 if mobile else 145,'source':160 if mobile else 145};h=heights[kind]
 title={'hero':'AiCoN. Useful tech. Clear answers.','activity':'Website main-branch commits over fourteen UTC days, including automation','calendar':'Ninety-one-day public GitHub account calendar. Decorative moving trail.','guides':'Read the guides','community':'Join the community','source':'Explore the source'}[kind]
 css=FONT+f' :root{{color-scheme:{theme}}} text{{font-family:Outfit,Arial,sans-serif;fill:{c["ink"]}}} .muted{{fill:{c["muted"]}}} .orange{{fill:{ORANGE}}} .rise{{animation:rise .9s ease-out both}} .drift{{animation:drift 6s ease-in-out infinite}} .bar{{transform-box:fill-box;transform-origin:bottom;animation:grow 1.2s cubic-bezier(.2,.7,.2,1) both}} @keyframes grow{{from{{transform:scaleY(.08)}}to{{transform:scaleY(1)}}}} @keyframes drift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}} @keyframes rise{{from{{opacity:.8;transform:translateY(7px)}}to{{opacity:1;transform:translateY(0)}}}} @media(prefers-reduced-motion:reduce){{*{{animation:none!important}} .motion{{display:none}}}}'
 css+=' .signal{transform-box:fill-box;transform-origin:center;animation:signal 8s ease-in-out infinite}.arrow{animation:nudge 2.8s ease-in-out infinite}.bar{animation:grow 1.2s ease-out both,shine 3.6s ease-in-out infinite;animation-delay:0s,var(--delay)}.cell{animation:shimmer 5s ease-in-out infinite;animation-delay:var(--delay)}.orbit{transform-box:fill-box;transform-origin:center;animation:beacon 2.4s ease-in-out infinite}@keyframes signal{0%,35%{transform:rotate(0)}70%,100%{transform:rotate(90deg)}}@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(7px)}}@keyframes shine{0%,100%{opacity:1}50%{opacity:.48}}@keyframes shimmer{0%,65%,100%{opacity:1}82%{opacity:.48}}@keyframes beacon{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.65)}}@media(prefers-reduced-motion:reduce){*{animation:none!important}.motion{display:none}}'
 if STATIC:css+=' *{animation:none!important}.motion{display:none}'
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{title}</title><desc id="desc">Original AiCoN card. Public data checked {s["checked_at_ist"]}. Reduced motion supported.</desc><style>{css}</style><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22" fill="{c["bg"]}" stroke="{c["rule"]}"/>']
 if kind=='hero':
  logo=(OUT/'brand-lockup.svg').read_text();body=logo[logo.index('<g '):logo.rindex('</svg>')].replace('#111827',c['ink']);parts.append(f'<g transform="translate({pad} 30) scale(.046)">{body}</g>')
  parts.append(text(pad,120 if mobile else 154,'Useful tech.',50 if mobile else 73,700,extra='class="rise" letter-spacing="-2"'))
  parts.append(text(pad,174 if mobile else 231,'Clear answers.',50 if mobile else 73,700,extra='class="rise" letter-spacing="-2"'))
  y=218 if mobile else 275
  for i,line in enumerate(['Source-checked guides for','Kerala and India.']if mobile else ['Source-checked guides for Kerala and India.']):parts.append(text(pad,y+i*28,line,23 if mobile else 25,extra='class="muted"'))
  if mobile:
   parts.append(f'<rect x="24" y="307" width="372" height="108" rx="16" fill="{c["soft"]}"/>');base=360;parts.append(text(42,338,'FIND. READ. CHOOSE.',17,600,extra='class="muted"'));parts.append(text(42,389,'Your Trusted Tech Companion',22,600))
   parts.append(f'<circle class="drift" cx="365" cy="337" r="8" fill="{ORANGE}"/>')
  else:
   parts.append(text(pad,331,'Your Trusted Tech Companion',20,600,extra='class="muted"'))
   # A guide signal, not a fake data chart.
   parts.append(f'<g transform="translate(670 57)"><g class="drift"><circle cx="55" cy="44" r="42" fill="{c["sage"]}"/><path class="signal" d="M35 44h40M55 24v40" stroke="{c["bg"]}" stroke-width="6"/><circle class="orbit" cx="95" cy="1" r="10" fill="{ORANGE}"/></g></g>')
 elif kind=='activity':
  a=s['activity'];days=a['commit_days'];m=max(d['count'] for d in days)or 1
  parts.append(text(pad,42,'THE BUILD PULSE',17,600,extra='class="muted" letter-spacing="2"'))
  parts.append(text(pad,97,a['commit_total'],50,700));parts.append(text(150 if mobile else 174,92,'website commits / 14 UTC days',16 if mobile else 24))
  x0=pad;span=w-2*pad;bw=span/14
  floor=251 if mobile else 211;gh=110 if mobile else 84
  for i,d in enumerate(days):
   barh=max(3,gh*d['count']/m);colour=ORANGE if d['count']==m else (c['sage']if d['count']else c['rule']);x=x0+i*bw
   parts.append(f'<rect class="bar" style="--delay:{i*.16:.2f}s" x="{x:.1f}" y="{floor-barh:.1f}" width="{bw-6:.1f}" height="{barh:.1f}" rx="3" fill="{colour}"><title>{d["date"]}: {d["count"]} commits</title></rect>')
  parts.append(text(pad,floor+24,days[0]['date'],15,extra='class="muted"'));parts.append(text(w-pad,floor+24,days[-1]['date'],15,extra='class="muted" text-anchor="end"'))

 elif kind=='calendar':
  a=s['activity'];days=a['calendar'];parts.append(text(pad,42,'THE PUBLIC CALENDAR',17,600,extra='class="muted" letter-spacing="2"'));parts.append(text(pad,80,'91 days of aicon-hub',28 if mobile else 35,600))
  gx=pad;gy=104;step=(w-2*pad)/13;cell=min(17 if mobile else 14,step-5);rowgap=cell+5
  palette=[c['soft'],'#78503a','#a84f29','#df622c',ORANGE]
  for i,d in enumerate(days):
   x=gx+(i//7)*step;y=gy+(i%7)*rowgap
   parts.append(f'<rect class="cell" style="--delay:{(i//7)*.24+(i%7)*.06:.2f}s" x="{x:.1f}" y="{y}" width="{step-5:.1f}" height="{cell}" rx="3" fill="{palette[d["level"]]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>')
  parts.append(text(pad,h-23,days[0]['date']+' to '+days[-1]['date'],15,extra='class="muted"'))
  if not STATIC:
   # The moving highlight is intentionally separate from the contribution cells.
   parts.append(f'<circle class="motion" cx="0" cy="0" r="4" fill="{ORANGE}"><animateMotion dur="12s" repeatCount="indefinite" path="M{pad},{h-68} L{w-pad},{h-68} L{pad},{h-68}"/></circle>')
 else:
  labels={'guides':('01 / THE GUIDES','Read. Check. Decide.',f'{s["archive_entries"]} public guide links in the archive.','AI, apps, safety and opportunities.'),'community':('02 / THE COMMUNITY','Keep the useful stuff close.','Updates on WhatsApp and Telegram.','For everyday users, students and builders.'),'source':('03 / THE SOURCE','Built in the open.','Explore AiCoN\'s public repositories.','Website, apps and experiments.')};label,headline,sub,sub2=labels[kind]
  parts.append(text(pad,33,label,15,600,extra='class="muted" letter-spacing="1.6"'));parts.append(text(pad,75,headline,28 if mobile else 36,600,extra='letter-spacing="-.6"'));parts.append(text(pad,108,sub,18 if mobile else 22));parts.append(text(pad,135 if mobile else 133,sub2,16 if mobile else 18,extra='class="muted"'));parts.append(f'<path class="arrow" d="M{w-57} 33h22m-9-9 9 9-9 9" stroke="{ORANGE}" stroke-width="3" fill="none"/>')
 parts.append('</svg>');return ''.join(parts)

def picture(kind,alt,href=None):
 # Explicit theme sources work with GitHub's theme controls, not only OS theme.
 p=f'<picture>\n  <source media="(prefers-reduced-motion: reduce) and (max-width: 600px) and (prefers-color-scheme: dark)" srcset="cards/{kind}-mobile-dark-static.svg">\n  <source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="cards/{kind}-mobile-light-static.svg">\n  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="cards/{kind}-dark-static.svg">\n  <source media="(prefers-reduced-motion: reduce)" srcset="cards/{kind}-light-static.svg">\n  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="cards/{kind}-mobile-dark.svg">\n  <source media="(max-width: 600px)" srcset="cards/{kind}-mobile-light.svg">\n  <source media="(prefers-color-scheme: dark)" srcset="cards/{kind}-dark.svg">\n  <img src="cards/{kind}-light.svg" alt="{alt}" width="100%">\n</picture>'
 return ('<a href="'+href+'">\n'+p+'\n</a>')if href else p

def main():
 global STATIC
 original_static=STATIC
 s=json.loads((ROOT/'data/public-snapshot.json').read_text());OUT.mkdir(exist_ok=True)
 for kind in ['hero','activity','calendar','guides','community','source']:
  for theme in THEMES:
   for mobile in [False,True]:
    STATIC=original_static
    (OUT/f'{kind}{"-mobile"if mobile else ""}-{theme}.svg').write_text(svg(kind,theme,mobile,s))
    STATIC=True
    (OUT/f'{kind}{"-mobile"if mobile else ""}-{theme}-static.svg').write_text(svg(kind,theme,mobile,s))
 STATIC=original_static
 latest='<br>\n'.join('<a href="'+html.escape(p['url'],quote=True)+'">'+html.escape(p['title'])+'</a>' for p in s['latest'])
 md=picture('hero','AiCoN. Useful tech. Clear answers. Source-checked guides for Kerala and India.','https://aicon-hub.github.io/')+'\n\n<p align="center"><a href="https://aicon-hub.github.io/"><img src="cards/icons/website.svg" width="44" height="44" alt="AiCoN website"></a> <a href="https://whatsapp.com/channel/0029VawGIGTD38CRJde0fl1c"><img src="cards/icons/whatsapp.svg" width="44" height="44" alt="AiCoN WhatsApp channel"></a> <a href="https://t.me/AiCoN4tech"><img src="cards/icons/telegram.svg" width="44" height="44" alt="AiCoN Telegram channel"></a> <a href="mailto:aicon4tech@gmail.com"><img src="cards/icons/gmail.svg" width="44" height="44" alt="Email AiCoN on Gmail"></a> <a href="mailto:aicon4tech@proton.me"><img src="cards/icons/protonmail.svg" width="44" height="44" alt="Email AiCoN on Proton Mail"></a></p>\n\n'+picture('guides',f'Read the guides. {s["archive_entries"]} public archive links.','https://aicon-hub.github.io/posts/')+'\n\n'+picture('activity','Website main-branch commits over 14 UTC days, including automation.')+'\n\n'+picture('calendar','91-day public GitHub calendar. Colour levels are not website commit totals.')+'\n\n'
 md+=picture('community','Join AiCoN updates on WhatsApp.','https://whatsapp.com/channel/0029VawGIGTD38CRJde0fl1c')+'\n\n<p align="center"><a href="https://t.me/AiCoN4tech">Prefer Telegram? Follow AiCoN4tech</a></p>\n\n'+picture('source','Explore public AiCoN repositories.','https://github.com/aicon-hub?tab=repositories')+'\n\n<h3 align="center">Fresh from the guide library</h3>\n\n<p align="center">'+latest+'</p>\n\n'
 md+='<p align="center"><a href="https://aicon-hub.github.io/posts/about-aicon.html">About AiCoN</a> · <a href="mailto:aicon4tech@proton.me">Corrections and contact</a></p>\n'
 (ROOT/'README.md').write_text(md)
if __name__=='__main__':main()
