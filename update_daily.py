from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
import html, json, re, subprocess, xml.etree.ElementTree as ET

FEEDS = {'world':'https://feeds.bbci.co.uk/news/world/rss.xml','technology':'https://feeds.bbci.co.uk/news/technology/rss.xml','business':'https://feeds.bbci.co.uk/news/business/rss.xml','football':'https://feeds.bbci.co.uk/sport/football/rss.xml','nfl':'https://feeds.bbci.co.uk/sport/american-football/rss.xml','spurs':'https://feeds.bbci.co.uk/sport/football/teams/tottenham-hotspur/rss.xml','bills':'https://www.buffalobills.com/rss/news','bucs':'https://www.buccaneers.com/rss/news','aggies':'https://www.espn.com/espn/rss/ncf/news'}
SCHEDULES = {'spurs':('soccer/all','367'), 'aggies':('football/college-football','245'), 'bills':('football/nfl','2'), 'bucs':('football/nfl','27')}

def normalize_game(event, team_id):
    competition=event['competitions'][0]
    own=next(c for c in competition['competitors'] if str(c['id'])==team_id)
    opponent=next(c for c in competition['competitors'] if str(c['id'])!=team_id)
    moment=datetime.fromisoformat(event['date'].replace('Z','+00:00'))
    status=competition.get('status',{}).get('type',{})
    def score(c):
        value=c.get('score')
        return value.get('displayValue') if isinstance(value,dict) else str(value) if value is not None else None
    return {'id':event['id'],'date':moment.isoformat(),'day':moment.astimezone(ZoneInfo('America/New_York')).date().isoformat(),
            'opponent':opponent['team']['displayName'],'home':own['homeAway']=='home','status':status.get('state','pre'),
            'detail':status.get('shortDetail','Scheduled'),'completed':status.get('completed',False),
            'timeTBD':not competition.get('timeValid',event.get('timeValid',True)) or competition.get('status',{}).get('isTBDFlex',False),
            'score':score(own),'opponentScore':score(opponent),'venue':competition.get('venue',{}).get('fullName',''),
            'tv':list(dict.fromkeys(b['media']['shortName'] for b in competition.get('broadcasts',[]) if b.get('region')=='us' and b.get('media',{}).get('shortName')))}

def fetch_schedule(pair):
    name,(sport,team_id)=pair
    try:
        base=f'https://site.api.espn.com/apis/site/v2/sports/{sport}/teams/{team_id}/schedule'
        events={}
        for url in ([base,base+'?fixture=true'] if name=='spurs' else [base]):
            raw=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','25',url],check=True,capture_output=True).stdout
            if len(raw)>4000000: raise ValueError('Schedule too large')
            payload=json.loads(raw)
            if str(payload['team']['id'])!=team_id: raise ValueError('Unexpected team')
            for event in payload.get('events',[]): events[event['id']]=normalize_game(event,team_id)
        return name,{'status':'ok','items':sorted(events.values(),key=lambda g:g['date']),'source':'ESPN','checked':datetime.now(ZoneInfo('UTC')).isoformat()}
    except Exception as error:
        print(name,'schedule',type(error).__name__)
        return name,{'status':'unavailable','items':[]}

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
            summary=html.unescape(re.sub(r'<[^>]+>', ' ', item.findtext('description','')))
            summary=' '.join(summary.split())
            words=summary.split()
            summary=' '.join(words[:65])+('…' if len(words)>65 else '')
            try: published=parsedate_to_datetime(date)
            except (ValueError,TypeError): continue
            if published.tzinfo is None: published=published.replace(tzinfo=ZoneInfo('UTC'))
            host=urlparse(link).hostname or ''
            allowed={'bills':('buffalobills.com',),'bucs':('buccaneers.com',),'aggies':('espn.com',)}.get(name,('bbc.com','bbc.co.uk'))
            if urlparse(link).scheme != 'https' or not any(host==h or host.endswith('.'+h) for h in allowed): continue
            if not title or not now-timedelta(days=3)<=published<=now+timedelta(minutes=10): continue
            if name=='aggies' and not re.search(r'texas a&m|texas a&amp;m', title+' '+summary, re.I): continue
            source={'bills':'Buffalo Bills','bucs':'Tampa Bay Buccaneers','aggies':'ESPN','spurs':'BBC Sport','football':'BBC Sport','nfl':'BBC Sport'}.get(name,'BBC News')
            items.append({'title':title,'summary':summary,'url':link,'published':published.isoformat(),'source':source})
        if not items:
            return name,{'items':[],'status':'no_recent_stories','checked':now.isoformat()}
        items.sort(key=lambda x:x['published'],reverse=True)
        return name,{'items':items[:12],'status':'ok','checked':now.isoformat()}
    except Exception as error:
        print(name, type(error).__name__)
        return name,{'items':[],'status':'unavailable'}

def main():
    now=datetime.now(ZoneInfo('America/New_York'))
    feeds=dict(ThreadPoolExecutor(max_workers=9).map(fetch,FEEDS.items()))
    if not any(v['items'] for v in feeds.values()): raise RuntimeError('All feeds failed; preserving previous deployment')
    schedules=dict(ThreadPoolExecutor(max_workers=4).map(fetch_schedule,SCHEDULES.items()))
    data={'edition':now.date().isoformat(),'updated':now.isoformat(),'feeds':feeds,'schedules':schedules}
    Path('content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('Edition',data['edition'], 'ready:', sum(len(v['items']) for v in feeds.values()),'source headlines')

if __name__=='__main__': main()
