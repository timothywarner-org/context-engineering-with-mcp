"""Rebuild the root architecture SVGs and offline gallery using Python's standard library.

Run from any directory: python scripts/Build-Architecture.py
The official Azure icons are embedded without changing their artwork.
PNG exports are presentation conveniences; the SVGs remain the editable source.
"""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
INK = "#172840"
MUTED = "#455871"
BLUE = "#1467D2"
PURPLE = "#7047B8"
AMBER = "#A85D0C"


def rect(x, y, w, h, fill="white", stroke="#CCD7E5", radius=22, sw=2, dash=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'


def text(x, y, value, size=30, color=INK, weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="sans-serif" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def lines(x, y, values, size=30, step=42, color=INK, weight=400, anchor="start"):
    return ''.join(text(x,y+i*step,v,size,color,weight,anchor) for i,v in enumerate(values))


def arrow(points, color=BLUE, both=False, dashed=False):
    coords=[tuple(map(float,p.split(','))) for p in points.split()]
    def head(tip,prev):
        x,y=tip;dx,dy=x-prev[0],y-prev[1];length=(dx*dx+dy*dy)**.5;ux,uy=dx/length,dy/length
        return f'<polygon points="{x},{y} {x-15*ux+7*uy},{y-15*uy-7*ux} {x-15*ux-7*uy},{y-15*uy+7*ux}" fill="{color}"/>'
    return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round"' + (' stroke-dasharray="10 8"' if dashed else '') + '/>' + head(coords[-1],coords[-2]) + (head(coords[0],coords[1]) if both else '')


def icon(name, x, y, size=80):
    source=(ROOT / "images/architecture" / f"{name}.svg").read_text(encoding="utf-8")
    source=re.sub(r'<\?xml[^>]*\?>','',source)
    artwork=re.sub(r'^\s*<svg[^>]*>','',source)
    artwork=re.sub(r'</svg>\s*$','',artwork)
    return f'<g transform="translate({x},{y}) scale({size/18})">{artwork}</g>'


def page(number, title, subtitle, content, takeaway, description):
    defs=''.join(f'<marker id="arrow-{c[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker><marker id="back-{c[1:]}" markerWidth="10" markerHeight="10" refX="2" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M10 0 L0 5 L10 10 Z" fill="{c}"/></marker>' for c in [BLUE,PURPLE,AMBER,MUTED])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1920 1080" width="1920" height="1080" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>{defs}</defs><g font-family="Arial, Helvetica, sans-serif">
{rect(0,0,1920,1080,'#F5F8FC','#F5F8FC',0)}
{rect(0,0,1920,182,'#122844','#122844',0)}
{text(64,53,'CONTEXT ENGINEERING WITH MCP   /   '+number,24,'#B6D7FF',700)}
{text(64,115,title,50,'white',700)}
{text(64,159,subtitle,27,'#E1ECFA')}
{content}
{rect(64,980,1792,64,'#E6EEF9','#E6EEF9',16)}
{text(960,1022,takeaway,29,INK,700,'middle')}
</g></svg>'''


def protocol():
    s=rect(64,220,800,720,'#EAF2FF','#8FB6EE',28)
    s+=text(104,276,'HOST APPLICATION',25,BLUE,700)
    s+=text(104,321,'Copilot, Claude, or your application',33,INK,700)
    s+=rect(104,365,420,145)+text(132,414,'Model',36,INK,700)
    s+=lines(132,457,['Receives selected context','Returns an answer or tool call'],25,33,MUTED)
    s+=rect(104,590,420,235,'white',BLUE)
    s+=text(132,637,'Context assembly',34,BLUE,700)
    s+=lines(132,686,['User goal + instructions','Selected results + evidence','Permissions + consent'],28,44)
    s+=arrow('314,590 314,510',BLUE,True)
    s+=text(336,559,'Host controls this',24,MUTED)
    s+=rect(584,376,240,112,'white',BLUE)+lines(704,422,['MCP client A','Incidents'],26,37,INK,700,'middle')
    s+=rect(584,652,240,112,'white',PURPLE)+lines(704,698,['MCP client B','Memory'],26,37,INK,700,'middle')
    s+=arrow('524,660 550,660 550,432 584,432',BLUE)
    s+=arrow('524,710 584,710',PURPLE)
    s+=text(104,897,'Each client connects to one server.',29,INK,700)
    s+=arrow('824,432 1110,432',BLUE,True)+text(967,403,'stdio / JSON-RPC',25,BLUE,700,'middle')
    s+=arrow('824,708 1110,708',PURPLE,True)+text(967,680,'stdio / JSON-RPC',25,PURPLE,700,'middle')
    s+=rect(1110,240,746,338,'white',BLUE,26,3)
    s+=text(1146,292,'Incident MCP server',36,BLUE,700)
    s+=text(1146,334,'Python starter or TypeScript alternative',26,MUTED)
    s+=lines(1146,392,['TOOL       get_incident(INC-1042)','RESOURCE   Order API runbook','PROMPT     investigate_incident'],29,63)
    s+=rect(1110,625,746,205,'white',PURPLE,26,3)
    s+=text(1146,675,'Memory MCP server',36,PURPLE,700)
    s+=lines(1146,726,['memory_write  /  memory_search','memory_compress'],29,45)
    s+=arrow('1483,830 1483,874',PURPLE,True)
    s+=rect(1250,874,466,66,'#F1EAFE','#BBA2E0',14)+text(1483,917,'Durable local JSON file',29,PURPLE,700,'middle')
    return page('01','MCP connects capabilities. The host builds context.',
                'The course uses local stdio servers. Remote servers can use HTTP; the responsibilities stay distinct.',s,
                'A tool result becomes model context only when the host includes it.',
                'A host contains a model, context assembly, and two distinct MCP clients. Client A communicates with the incident server; client B communicates with the memory server backed by a local JSON file. The host chooses context and permissions.')


def memory():
    s=rect(64,232,760,488,'#EAF2FF','#8FB6EE',26)
    s+=text(100,284,'PROCESS A  /  CAPTURE',27,BLUE,700)
    s+=rect(100,316,688,138)+text(130,363,'Retrieve incident facts + runbook',32,INK,700)
    s+=lines(130,405,['INC-1042  ·  Order API  ·  Priya Patel'],29,40)
    s+=arrow('444,454 444,486',BLUE)
    s+=rect(100,486,688,190,'white',BLUE)+text(130,535,'memory_write',33,BLUE,700)
    s+=lines(130,582,['Save a useful decision with tags.','Keep the approval requirement.'],30,45)
    s+=rect(1096,232,760,488,'#F1EAFE','#BBA2E0',26)
    s+=text(1132,284,'PROCESS B  /  REUSE',27,PURPLE,700)
    s+=rect(1132,316,688,138)+text(1162,363,'memory_search + memory_compress',32,PURPLE,700)
    s+=text(1162,411,'Rank matches. Select and truncate.',29,INK)
    s+=arrow('1476,454 1476,486',PURPLE)
    s+=rect(1132,486,688,190,'white',PURPLE)+text(1162,535,'Assemble the next model request',32,INK,700)
    s+=lines(1162,582,['The host explicitly includes the result.','Review sources, dates and caveats.'],29,45)
    s+=f'<line x1="960" y1="235" x2="960" y2="705" stroke="#AAB8CA" stroke-width="3" stroke-dasharray="10 10"/>'
    s+=rect(844,404,232,147,'#F5F8FC','#F5F8FC',14)
    s+=lines(960,446,['A exits.','B starts fresh.','The file survives.'],25,39,INK,700,'middle')
    s+=rect(690,784,540,152,'white',PURPLE,24,3)
    s+=text(960,830,'DURABLE JSON STORE',27,PURPLE,700,'middle')
    s+=lines(960,873,['Same absolute path in both processes','Separate from chat history'],26,37,INK,400,'middle')
    s+=arrow('444,720 444,860 690,860',BLUE)
    s+=text(478,827,'1  WRITE',27,BLUE,700)
    s+=arrow('1230,860 1476,860 1476,720',PURPLE)
    s+=text(1263,827,'2  RETRIEVE',27,PURPLE,700)
    return page('02','Memory survives a process. Context must be rebuilt.',
                'The scripted demo proves persistence and retrieval. A fresh host conversation completes model-facing reuse.',s,
                'Storage persists. Retrieval selects. The host decides what the model sees.',
                'Process A retrieves incident evidence and saves a decision via memory_write to a durable JSON file. After A exits, process B searches and compresses from the same file, then the host includes that result in a new model request. Compression selects and truncates; it is not an LLM summary.')


def azure():
    s=rect(64,402,300,206,'white',BLUE,24,3)
    s+=lines(214,457,['MCP client','in your host'],34,48,INK,700,'middle')
    s+=text(214,566,'tools/list or tools/call',24,MUTED,400,'middle')
    s+=text(64,329,'HTTPS + subscription key',27,BLUE,700)
    s+=arrow('364,505 475,505',BLUE,True)
    s+=rect(475,225,590,708,'#EAF2FF','#8FB6EE',26)
    s+=icon('api-management',507,252,80)
    s+=text(609,286,'Azure API Management',33,BLUE,700)
    s+=text(609,327,'Authenticate, route, deny, limit',25,MUTED)
    s+=rect(507,374,526,92)+text(534,411,'tools/list',30,INK,700)+text(534,445,'Discover the catalog',25,MUTED)
    s+=rect(507,492,526,92)+text(534,529,'get_incident',30,INK,700)+text(534,563,'Route by the request body',25,MUTED)
    s+=rect(507,610,526,112)+text(534,648,'get_runbook',30,INK,700)+text(534,688,'Policy: 2 calls / 60 s; excess → 429',25,MUTED)
    s+=rect(507,758,526,137,'#FFF2E0','#C88635',18)
    s+=text(534,801,'request_rollback → 403',30,AMBER,700)
    s+=lines(534,842,['Denied at the gateway.','Fixture cannot roll back a real service.'],24,32)
    s+=rect(1220,225,636,708,'#EDF5FB','#83B4D9',26)
    s+=icon('container-apps',1252,252,80)
    s+=text(1354,286,'Azure Container Apps',33,BLUE,700)
    s+=text(1354,327,'ONE container, THREE endpoints',25,MUTED)
    for y,title,detail in [(374,'/catalog/mcp','Definitions for three tools'),(492,'/incidents/mcp','servedBy: incidents'),(610,'/runbooks/mcp','servedBy: runbooks')]:
        s+=rect(1252,y,572,92 if y<600 else 112)+text(1280,y+38,title,31,INK,700)+text(1280,y+73,detail,25,MUTED)
    s+=arrow('1033,420 1252,420',BLUE)
    s+=arrow('1033,538 1252,538',BLUE)
    s+=arrow('1033,666 1252,666',BLUE)
    s+=lines(1142,790,['Separate','backend key'],24,33,BLUE,700,'middle')
    s+=rect(1252,758,572,137,'white','#83B4D9',18)
    s+=lines(1280,803,['No backend key → 401','Direct access still requires authentication.'],26,43,INK,700)
    return page('03','One gateway. One container. Three MCP endpoints.',
                'The Azure supplement routes real requests and returns evidence of the endpoint that executed each tool.',s,
                'This demo uses keys. OAuth, per-user RBAC and private networking are extensions.',
                'A host MCP client sends HTTPS requests with a subscription key to Azure API Management. Discovery routes to catalog, incident calls to incidents, and rate-limited runbook calls to runbooks, all inside one Container Apps container. APIM denies rollback with 403 and forwards an independent backend credential. Direct backend calls without that credential return 401. Rate limiting is approximate.')


PAGES=[('ARCHITECTURE-01-mcp','Host, clients and servers',protocol),
       ('ARCHITECTURE-02-memory','Persistence and explicit context reuse',memory),
       ('ARCHITECTURE-03-azure','APIM routing and Container Apps',azure)]


def main():
    for stem, title, build in PAGES:
        (ROOT/f'{stem}.svg').write_text(build(),encoding='utf-8')
    cards=''.join(f'<section id="diagram-{i}"><h2>{i:02d}. {escape(title)}</h2><a class="image" href="{stem}.svg"><img src="{stem}.svg" alt="{escape(title)}"></a><p><a href="{stem}.svg" download>Download SVG</a> <a href="{stem}.png" download>Download PNG</a></p></section>' for i,(stem,title,_) in enumerate(PAGES,1))
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MCP architecture gallery</title><style>
    *{box-sizing:border-box}body{margin:0;background:#101e33;color:#e5eefc;font-family:Arial,Helvetica,sans-serif}header{max-width:1600px;margin:auto;padding:36px 36px 16px}h1{font-size:clamp(32px,4vw,56px);margin:0 0 12px}header p{font-size:22px;line-height:1.5;margin:0}nav{display:flex;gap:16px;flex-wrap:wrap;padding:20px 0}a{color:#b9d9ff;text-underline-offset:5px}nav a,button{font-size:20px;color:#fff;background:#28496f;padding:12px 18px;border:1px solid #6d92bf;border-radius:10px;text-decoration:none}button{cursor:pointer}main{max-width:1920px;margin:auto}section{padding:12px 32px 32px;scroll-margin-top:15px}h2{font-size:28px;margin:16px 0}img{width:100%;height:auto;display:block;border-radius:14px;background:#f5f8fc}section p{font-size:20px;display:flex;gap:30px}footer{padding:0 36px 36px;font-size:20px;line-height:1.6}a:focus-visible,button:focus-visible{outline:4px solid #ffd07a;outline-offset:5px}@media print{body{background:#fff;color:#172840}header,nav,footer,section p,h2{display:none}section{padding:0;break-after:page}img{border-radius:0}@page{size:landscape;margin:0}}
    </style><header><h1>MCP architecture, made visible</h1><p>Three readable views of the fictional WARNERCO incident workflow. Offline, scalable, and ready to project.</p><nav><a href="#diagram-1">01 Protocol</a><a href="#diagram-2">02 Memory</a><a href="#diagram-3">03 Azure</a><button id="full">Full screen</button><a href="ARCHITECTURE.md">Sources and teaching notes</a></nav></header><main>'''+cards+'''</main><footer>Use the SVGs for sharp scaling. PNGs are 3840 × 2160. Azure icons are Microsoft's official artwork; see the attribution in ARCHITECTURE.md.</footer><script>document.getElementById('full').onclick=()=>{if(document.fullscreenElement){document.exitFullscreen()}else{document.documentElement.requestFullscreen().catch(()=>{})}};</script></html>'''
    (ROOT/'ARCHITECTURE.html').write_text(html,encoding='utf-8')
    print('Generated three 1920 x 1080 SVGs and the offline architecture gallery.')


if __name__=='__main__':
    main()
