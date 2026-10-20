"""Refresh public AiCoN profile data. No analytics or visitor collection."""
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import activity
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SITE = 'https://aicon-hub.github.io/'
INDEX = SITE + 'posts/index.html'
REPO_API = 'https://api.github.com/repos/aicon-hub/aicon-hub.github.io'


def get(url):
    req = Request(url, headers={'User-Agent': 'AiCoN-public-profile/1.0', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'text/html'})
    with urlopen(req, timeout=30) as response:
        data = response.read(4_000_001)
        if len(data) > 4_000_000:
            raise ValueError('Public source exceeds expected size')
        return response.status, data.decode('utf-8')


class GuideIndex(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_index = False
        self.in_link = False
        self.current = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'ul' and attrs.get('id') == 'postlist':
            self.in_index = True
        if self.in_index and tag == 'a':
            url = urljoin(INDEX, attrs.get('href', ''))
            parsed = urlparse(url)
            if parsed.netloc == 'aicon-hub.github.io' and parsed.path.startswith('/posts/') and parsed.path.endswith('.html') and parsed.path != '/posts/index.html':
                self.current = {'title': '', 'url': url}
                self.in_link = True

    def handle_data(self, data):
        if self.in_link:
            self.current['title'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            self.current['title'] = ' '.join(self.current['title'].split())
            self.rows.append(self.current)
            self.in_link = False
        if tag == 'ul' and self.in_index:
            self.in_index = False


def safe_md(value):
    return re.sub(r'([\\`*_{}\[\]<>|])', r'\\\1', value).replace('\n', ' ')


def dashboard(snapshot):
    esc = html.escape
    cells = [('ARCHIVE ENTRIES', str(snapshot['archive_entries'])), ('HOMEPAGE CHECK', 'HTTP '+str(snapshot['homepage_status'])), ('SITE REPO STARS', str(snapshot['stars'])), ('SITE REPO FORKS', str(snapshot['forks']))]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="520" height="405" viewBox="0 0 520 405" role="img"><title>AiCoN public activity snapshot</title>', '<rect width="520" height="405" rx="20" fill="#101319"/>', '<rect x="22" y="25" width="4" height="27" rx="2" fill="#ff682f"/>', '<g font-family="Inter,Arial,sans-serif">', '<text x="38" y="46" fill="#fff" font-size="21" font-weight="700">PUBLIC ACTIVITY</text>', '<text x="22" y="80" fill="#aeb7c4" font-size="17">Public sources. No visitor tracking.</text>']
    for i,(label,value) in enumerate(cells):
        x = 22 + (i % 2)*244
        y = 104 + (i // 2)*105
        parts += [f'<rect x="{x}" y="{y}" width="232" height="92" rx="12" fill="#1c222c"/>',f'<text x="{x+15}" y="{y+30}" fill="#aeb7c4" font-size="17" font-weight="600">{label}</text>',f'<text x="{x+15}" y="{y+73}" fill="#ff682f" font-size="34" font-weight="700">{esc(value)}</text>']
    parts += [f'<text x="22" y="335" fill="#fff" font-size="17">{esc(snapshot["checked_at_ist"])}</text>',f'<text x="22" y="360" fill="#aeb7c4" font-size="16">{esc(snapshot["checked_at_utc"])}</text>','<text x="22" y="385" fill="#aeb7c4" font-size="16">Hourly target, not real-time</text>','</g></svg>']
    return ''.join(parts)


def apply_snapshot(snapshot):
    readme = ROOT / 'README.md'
    text = readme.read_text()
    summary = f'![Public activity dashboard](assets/public-dashboard.svg)\n\nChecked **{snapshot["checked_at_ist"]}** ({snapshot["checked_at_utc"]}).\n\n**{snapshot["archive_entries"]} archive entries** · **Homepage HTTP {snapshot["homepage_status"]}** · **{snapshot["stars"]} site-repo star(s)** · **{snapshot["forks"]} site-repo fork(s)**'
    latest = '\n'.join(f'- [{safe_md(p["title"])}]({p["url"]})' for p in snapshot['latest'])
    commits = '\n'.join(f'- [`{c["sha"][:7]}`]({c["url"]}) · {c["date_utc"]} · {safe_md(c["title"])}' for c in snapshot['activity']['commits'])
    commit_days = snapshot['activity']['commit_days']
    activity_text = f'![Site main-branch commit activity](assets/commit-activity.svg)\n\n**{snapshot["activity"]["commit_total"]} reachable main-branch commits** from **{commit_days[0]["date"]}** through **{commit_days[-1]["date"]}** (UTC dates; the current day is partial).\n\n' + commits + '\n\n[Open the website commit history](https://github.com/aicon-hub/aicon-hub.github.io/commits/main/)'
    activity_text = f'![Website commit graph](assets/commit-activity.svg)\n\n**{snapshot["activity"]["commit_total"]} website-repo main-branch commits** · 14 UTC days · includes automation.'
    latest = '\n'.join(latest.splitlines()[:3])
    for key, body in [('SNAPSHOT',summary),('LATEST',latest),('ACTIVITY',activity_text),('COMMITS',commits)]:
        pattern = rf'(<!-- AICON:{key}:START -->).*?(<!-- AICON:{key}:END -->)'
        if len(re.findall(pattern,text,flags=re.S)) != 1:
            raise ValueError('Missing or duplicate generated section')
        text = re.sub(pattern,lambda m:m[1]+'\n'+body+'\n'+m[2],text,flags=re.S)
    (ROOT/'assets').mkdir(exist_ok=True)
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'assets/public-dashboard.svg').write_text(dashboard(snapshot))
    (ROOT/'assets/commit-activity.svg').write_text(activity.commit_graph(snapshot['activity']))
    (ROOT/'assets/account-activity.svg').write_text(activity.calendar_svg(snapshot['activity']))
    (ROOT/'assets/contribution-snake.svg').write_text(activity.calendar_svg(snapshot['activity'],snake=True))
    activity.snake_gif(snapshot['activity'], ROOT/'assets/contribution-snake.gif')
    (ROOT/'data/public-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
    readme.write_text(text)


def main():
    homepage_status, homepage = get(SITE)
    _, index = get(INDEX)
    _, repo = get(REPO_API)
    if '<title>AiCoN' not in homepage:
        raise ValueError('Unexpected homepage content')
    parser = GuideIndex()
    parser.feed(index)
    rows = list({p['url']:p for p in reversed(parser.rows)}.values())
    rows.reverse()
    if not rows:
        raise ValueError('No guide entries found; refusing a false zero')
    repo = json.loads(repo)
    now = dt.datetime.now(dt.timezone.utc)
    snapshot = {'checked_at_utc':now.strftime('%Y-%m-%d %H:%M UTC'),'checked_at_ist':now.astimezone(dt.timezone(dt.timedelta(hours=5,minutes=30))).strftime('%d %b %Y, %I:%M %p IST'),'archive_entries':len(rows),'homepage_status':homepage_status,'stars':repo['stargazers_count'],'forks':repo['forks_count'],'latest':rows[:5],'sources':[SITE,INDEX,REPO_API]}
    if repo.get('full_name') != 'aicon-hub/aicon-hub.github.io':
        raise ValueError('Unexpected repository')
    snapshot['activity'] = activity.collect(now)
    snapshot['sources'] += [activity.HISTORY, activity.CALENDAR]
    apply_snapshot(snapshot)


if __name__ == '__main__':
    main()
