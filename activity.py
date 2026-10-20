"""Public activity renderers. The snake is a visual animation, not a metric."""
from collections import Counter
from datetime import datetime, timezone, timedelta
from html import escape
from html.parser import HTMLParser
import re
import subprocess
import tempfile
from urllib.request import Request, urlopen

HISTORY = 'https://github.com/aicon-hub/aicon-hub.github.io/commits/main/'
CALENDAR = 'https://github.com/users/aicon-hub/contributions'

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days=[]; self.tooltip=None; self.tips={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and a.get('data-date'):
            self.days.append({'date':a['data-date'],'level':int(a['data-level']),'id':a['id']})
        if tag=='tool-tip':self.tooltip=a.get('for'); self.tips[self.tooltip]=''
    def handle_data(self,data):
        if self.tooltip:self.tips[self.tooltip]+=data
    def handle_endtag(self,tag):
        if tag=='tool-tip':self.tooltip=None


def collect(now):
    since=now.date()-timedelta(days=13)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['git','clone','--bare','--filter=blob:none','--shallow-since='+(since-timedelta(days=2)).isoformat(),'--single-branch','--branch','main','https://github.com/aicon-hub/aicon-hub.github.io.git',tmp+'/repo'],check=True,capture_output=True,timeout=90)
        result=subprocess.run(['git','--git-dir='+tmp+'/repo','log','--format=%H%x09%cI%x09%s'],check=True,capture_output=True,text=True,timeout=30).stdout
    commits=[]
    for line in result.splitlines():
        sha,date,title=line.split('\t',2); stamp=datetime.fromisoformat(date).astimezone(timezone.utc)
        if since<=stamp.date()<=now.date():
            commits.append({'sha':sha,'url':'https://github.com/aicon-hub/aicon-hub.github.io/commit/'+sha,'date_utc':stamp.strftime('%d %b %Y, %H:%M UTC'),'day':stamp.date().isoformat(),'title':title})
    if not commits:raise ValueError('No public commits returned; refusing a false zero')
    counts=Counter(c['day'] for c in commits)
    days=[{'date':(since+timedelta(days=i)).isoformat(),'count':counts[(since+timedelta(days=i)).isoformat()]} for i in range(14)]
    req=Request(CALENDAR,headers={'User-Agent':'AiCoN-public-profile/1.0'})
    with urlopen(req,timeout=30) as response:markup=response.read().decode()
    parser=Calendar();parser.feed(markup)
    calendar=sorted([d for d in parser.days if d['date']<=now.date().isoformat()],key=lambda d:d['date'])[-91:]
    if len(calendar)!=91:raise ValueError('Unexpected contribution calendar format')
    for day in calendar:
        tip=parser.tips.get(day.pop('id'),'').strip();match=re.match(r'(\d+) contributions?',tip)
        if tip.startswith('No contributions'):day['count']=0
        elif match:day['count']=int(match[1])
        else:raise ValueError('Calendar tooltip missing; refusing to invent counts')
    return {'commit_days':days,'commits':commits[:5],'commit_total':len(commits),'calendar':calendar,'history_url':HISTORY,'calendar_url':CALENDAR}


def head(width,height,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" rx="18" fill="#101319"/><g font-family="Inter,Arial,sans-serif">']


def commit_graph(activity):
    parts=head(520,365,'Site main-branch commits per UTC day, including automation')
    parts+=['<text x="22" y="34" fill="#fff" font-size="21" font-weight="700">BUILD PULSE</text>','<text x="22" y="63" fill="#aeb7c4" font-size="17">Site main-branch commits · UTC days</text>']
    maximum=max(d['count'] for d in activity['commit_days']) or 1
    for i,d in enumerate(activity['commit_days']):
        x=28+i*34; h=170*d['count']/maximum
        parts += [f'<rect x="{x}" y="{270-h:.2f}" width="24" height="{max(h,2):.2f}" rx="3" fill="#ff682f"><title>{d["date"]}: {d["count"]} commits</title></rect>',f'<text x="{x+12}" y="{258-h:.2f}" fill="#edf0f5" text-anchor="middle" font-size="12">{d["count"]}</text>',f'<text x="{x+12}" y="293" fill="#aeb7c4" text-anchor="middle" font-size="13">{d["date"][-2:]}</text>']
    parts += [f'<text x="22" y="325" fill="#edf0f5" font-size="16">{activity["commit_days"][0]["date"]} to {activity["commit_days"][-1]["date"]}</text>','<text x="22" y="348" fill="#aeb7c4" font-size="15">Includes bots and receipt commits, not just articles.</text>','</g></svg>'];return ''.join(parts)


def calendar_svg(activity,snake=False):
    parts=head(520,380 if snake else 330,'Animated contribution snake' if snake else 'AiCoN account contribution calendar, 91 days')
    parts += [f'<text x="22" y="35" fill="#fff" font-size="21" font-weight="700">{"CONTRIBUTION SNAKE" if snake else "ACCOUNT ACTIVITY"}</text>','<text x="22" y="64" fill="#aeb7c4" font-size="16">91 days · GitHub public profile calendar</text>']
    palette=['#202833','#693321','#a64724','#d95c27','#ff8c43']
    coords=[]
    for i,d in enumerate(activity['calendar']):
        col=i//7;row=i%7;x=28+col*36;y=88+row*25
        parts.append(f'<rect x="{x}" y="{y}" width="29" height="19" rx="4" fill="{palette[d["level"]]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>')
    if snake:
        for col in range(13):
            for row in (range(7) if col%2==0 else range(6,-1,-1)):
                coords.append((28+col*36+14.5,88+row*25+9.5))
        path='M'+' L'.join(f'{x},{y}' for x,y in coords)
        for j in range(4):
            # A same-shaped finite loop with offset start times creates the tail.
            parts.append(f'<circle r="{8-j}" fill="{["#fff","#ffb184","#ff8c43","#ff682f"][j]}"><animateMotion dur="18s" repeatCount="indefinite" begin="-{j*.1}s" path="{path}"/></circle>')
    parts += [f'<text x="22" y="290" fill="#edf0f5" font-size="15">{activity["calendar"][0]["date"]} to {activity["calendar"][-1]["date"]}</text>','<text x="22" y="314" fill="#aeb7c4" font-size="15">Colour levels follow GitHub, not site commit totals.</text>']
    if snake:parts+=['<text x="22" y="344" fill="#ffad83" font-size="15">The moving snake is decorative, not extra activity.</text>','<text x="22" y="367" fill="#aeb7c4" font-size="15">Animation loops; the underlying data refreshes hourly.</text>']
    parts.append('</g></svg>');return ''.join(parts)


def snake_gif(activity, output):
    from PIL import Image, ImageDraw, ImageFont
    import math
    def font(size):
        paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
        for path in paths:
            try:return ImageFont.truetype(path,size)
            except OSError:pass
        return ImageFont.load_default()
    image=Image.new('RGB',(780,540),'#101319');draw=ImageDraw.Draw(image)
    draw.text((32,28),'THE CONTRIBUTION SNAKE',font=font(28),fill='#ffffff')
    draw.text((32,74),'aicon-hub · 91-day public GitHub calendar',font=font(21),fill='#aeb7c4')
    palette=['#202833','#693321','#a64724','#d95c27','#ff8c43']
    coords=[]
    for i,day in enumerate(activity['calendar']):
        col=i//7; row=i%7; x=38+col*55; y=126+row*40
        draw.rounded_rectangle((x,y,x+44,y+29),radius=5,fill=palette[day['level']])
    for col in range(13):
        for row in (range(7) if col%2==0 else range(6,-1,-1)):
            coords.append((60+col*55,140.5+row*40))
    draw.text((32,435),activity['calendar'][0]['date']+' to '+activity['calendar'][-1]['date'],font=font(21),fill='#ffffff')
    draw.text((32,474),'Real calendar levels · decorative motion',font=font(21),fill='#ffad83')
    draw.text((32,506),'Data refresh target: hourly, not real-time',font=font(19),fill='#aeb7c4')
    frames=[]
    for i in range(len(coords)):
        im=image.copy();d=ImageDraw.Draw(im)
        for j in reversed(range(min(5,i+1))):
            x,y=coords[(i-j)%len(coords)];radius=11-j
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=['#ffffff','#ffd2b6','#ffad83','#ff8c43','#ff682f'][j])
        x,y=coords[i];d.ellipse((x+2,y-5,x+5,y-2),fill='#101319');d.ellipse((x+2,y+2,x+5,y+5),fill='#101319')
        frames.append(im)
    frames[0].save(output,save_all=True,append_images=frames[1:],duration=150,loop=0,optimize=True)
