"""Fetch only public AiCoN data and render the profile. No authentication needed."""
import sys,json,re,datetime as dt
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import activity
SITE='https://aicon-hub.github.io/'
def get(url):
 with urlopen(Request(url,headers={'User-Agent':'AiCoN-public-profile/2.0'}),timeout=30) as r:
  b=r.read(4_000_001)
  if len(b)>4_000_000:raise ValueError('Unexpected response size')
  return r.status,b.decode()
class Guides(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.card=False;self.h3=False;self.link=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='article':self.card='guide-card' in a.get('class','').split()
  if self.card and tag=='h3':self.h3=True
  if self.card and self.h3 and tag=='a':self.link={'title':'','url':urljoin(SITE+'posts/',a.get('href',''))}
 def handle_data(self,data):
  if self.link is not None:self.link['title']+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.link is not None:
   p=urlparse(self.link['url']);self.link['title']=' '.join(self.link['title'].split())
   if p.netloc=='aicon-hub.github.io' and p.path.startswith('/posts/') and self.link['title']:self.rows.append(self.link)
   self.link=None
  if tag=='h3':self.h3=False
  if tag=='article':self.card=False

def main():
 status,home=get(SITE);_,markup=get(SITE+'posts/');_,raw=get('https://api.github.com/repos/aicon-hub/aicon-hub.github.io');repo=json.loads(raw)
 if status!=200 or repo.get('full_name')!='aicon-hub/aicon-hub.github.io':raise ValueError('Unexpected public source')
 p=Guides();p.feed(markup);rows=list({x['url']:x for x in p.rows}.values())
 if len(rows)<100:raise ValueError('Unexpected archive shape; preserving previous snapshot')
 now=dt.datetime.now(dt.timezone.utc);a=activity.collect(now)
 s={'checked_at_utc':now.strftime('%Y-%m-%d %H:%M UTC'),'checked_at_ist':now.astimezone(dt.timezone(dt.timedelta(hours=5,minutes=30))).strftime('%d %b %Y, %I:%M %p IST'),'archive_entries':len(rows),'homepage_status':status,'stars':repo['stargazers_count'],'forks':repo['forks_count'],'latest':rows[:3],'activity':a,'sources':[SITE,SITE+'posts/','https://api.github.com/repos/aicon-hub/aicon-hub.github.io',activity.HISTORY,activity.CALENDAR]}
 targets=[ROOT/'README.md',ROOT/'data/public-snapshot.json',*list((ROOT/'cards').glob('*.svg'))]
 previous={p:p.read_bytes() for p in targets if p.exists()}
 try:
  (ROOT/'data/public-snapshot.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
  import render_cards
  render_cards.main()
 except Exception:
  for path,raw in previous.items():path.write_bytes(raw)
  raise
 print('Public snapshot refreshed:',s['archive_entries'],'guide links,',a['commit_total'],'site commits in14UTCdays')
if __name__=='__main__':main()
