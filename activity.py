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
