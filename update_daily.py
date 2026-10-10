from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
import json, re, subprocess, xml.etree.ElementTree as ET

FEEDS = {'world':'https://feeds.bbci.co.uk/news/world/rss.xml','technology':'https://feeds.bbci.co.uk/news/technology/rss.xml','business':'https://feeds.bbci.co.uk/news/business/rss.xml','football':'https://feeds.bbci.co.uk/sport/football/rss.xml','nfl':'https://feeds.bbci.co.uk/sport/american-football/rss.xml'}

def fetch(pair):
    name,url=pair
    try:
        raw=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','25',url],check=True,capture_output=True).stdout
        if len(raw)>2000000: raise ValueError('Feed too large')
        root=ET.fromstring(raw)
        items=[]
        now=datetime.now(ZoneInfo('UTC'))
        for item in root.findall('./channel/item'):
            title=item.findtext('title','').strip()
            link=item.findtext('link','').strip()
            date=item.findtext('pubDate','')
            try: published=parsedate_to_datetime(date)
            except (ValueError,TypeError): continue
            if published.tzinfo is None: published=published.replace(tzinfo=ZoneInfo('UTC'))
            host=urlparse(link).hostname or ''
            allowed=('bbc.com','bbc.co.uk')
            if urlparse(link).scheme != 'https' or not any(host==h or host.endswith('.'+h) for h in allowed): continue
            if not title or not now-timedelta(days=3)<=published<=now+timedelta(minutes=10): continue
            items.append({'title':title,'url':link,'published':published.isoformat(),'source':'BBC Sport' if name in ('football','nfl') else 'BBC News'})
        if not items: raise ValueError('No recent headlines')
        return name,{'items':items[:12],'status':'ok','checked':now.isoformat()}
    except Exception as error:
        print(name, type(error).__name__)
        return name,{'items':[],'status':'unavailable'}

def main():
    now=datetime.now(ZoneInfo('America/New_York'))
    feeds=dict(ThreadPoolExecutor(max_workers=5).map(fetch,FEEDS.items()))
    if not any(v['items'] for v in feeds.values()): raise RuntimeError('All feeds failed; preserving previous deployment')
    data={'edition':now.date().isoformat(),'updated':now.isoformat(),'feeds':feeds}
    Path('content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('Edition',data['edition'], 'ready:', sum(len(v['items']) for v in feeds.values()),'source headlines')

if __name__=='__main__': main()
