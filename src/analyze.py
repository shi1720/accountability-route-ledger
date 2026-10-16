"""Descriptive census of one register, not a causal or effectiveness estimate."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import csv, json, io

ROOT=Path(__file__).resolve().parents[1]
REGION={'Kazakhstan','Kyrgyz Republic','Tajikistan','Turkmenistan','Uzbekistan','Mongolia'}
PHYSICAL={'Energy','Transport','Urban','Water','Rural Infrastructure and Agriculture Development','Health Infrastructure','Education Infrastructure'}

def read_csv(path):
    return list(csv.DictReader(io.StringIO(Path(path).read_text(encoding='utf-8'))))

def summary(rows):
    amount=sum((Decimal(r['usd_million']) for r in rows),Decimal(0))
    ppm=[r for r in rows if r['iam']=='AIIB PPM']
    return {'rows':len(rows),'usd_million':str(amount),'ppm_rows':len(ppm),
            'delegated_rows':len(rows)-len(ppm),
            'ppm_usd_million':str(sum((Decimal(r['usd_million']) for r in ppm),Decimal(0))),
            'by_iam':dict(Counter(r['iam'] for r in rows))}

def policy_error(rows, weighted=False, keys=('policy',)):
    groups=defaultdict(Counter)
    for r in rows:
        groups[tuple(r[k] for k in keys)][r['iam']] += Decimal(r['usd_million']) if weighted else 1
    return sum(sum(g.values())-max(g.values()) for g in groups.values())

def route(record):
    """Return only expressly recorded IAM. An unknown does not become a denial."""
    iam=record.get('iam')
    if not iam or not record.get('source_locator'):
        return {'status':'unresolved','iam':None}
    return {'status':'documented_designation','iam':iam}

if __name__=='__main__':
    rows=read_csv(ROOT/'data/register_2025.csv')
    region=[r for r in rows if r['member'] in REGION]
    scopes={'register':rows,'region':region,
            'regional_selected_sector_labels': [r for r in region if r['sector'] in PHYSICAL],
            'regional_energy_transport':[r for r in region if r['sector'] in {'Energy','Transport'}],
            'regional_energy':[r for r in region if r['sector']=='Energy'],
            'regional_energy_transport_excluding_cpbf':[r for r in region if r['sector'] in {'Energy','Transport'} and r['row']!='151'],
            'regional_generation':[r for r in region if r['sector']=='Energy' and r['row']!='151'],
            'regional_without_crf':[r for r in region if not r['sector'].startswith('CRF-')]}
    out={k:summary(v) for k,v in scopes.items()}
    out['regional_countries']={k:summary([r for r in region if r['member']==k]) for k in sorted(REGION)}
    out['global_policy_iam']={p:dict(Counter(r['iam'] for r in rows if r['policy']==p)) for p in sorted({r['policy'] for r in rows})}
    out['minimum_policy_only_errors']=policy_error(rows)
    out['minimum_policy_only_error_usd_million']=str(policy_error(rows,True))
    out['minimum_policy_and_financing_type_errors']=policy_error(rows,keys=('policy','financing_type'))
    owner={'ADB SPS':'ADB AM','EBRD ESP':'EBRD IPAM','EIB ESP':'EIB CM','IFC ESSP & PS':'IFC CAO',
           'WB ESSP':'WB IPN','WB ESF':'WB IPN','WB PforR Policy':'WB IPN','WB DPF Policy':'WB IPN','AIIB ESP':'AIIB PPM','AfDB ISP':'AfDB IRM'}
    out['policy_owner_shortcut_errors']=sum(owner[r['policy']]!=r['iam'] for r in rows)
    (ROOT/'results').mkdir(exist_ok=True)
    old=read_csv(ROOT/'data/register_2024.csv')
    key=lambda r:(r['member'],r['approval'],r['usd_million'],r['project'])
    old_index={key(r):r for r in old};new_index={key(r):r for r in rows}
    assert len(old_index)==len(old) and len(new_index)==len(rows)
    common=old_index.keys()&new_index.keys()
    out['snapshot_comparison']={'old_rows':len(old),'new_rows':len(rows),'matched':len(common),
       'policy_changes':[key(k) for k in rows if key(k) in common and old_index[key(k)]['policy']!=k['policy']],
       'iam_changes':[key(k) for k in rows if key(k) in common and old_index[key(k)]['iam']!=k['iam']],
       'unmatched_old':[old_index[k]['project'] for k in old_index.keys()-new_index.keys()],
       'new_regional_projects':[r for r in region if key(r) not in old_index]}
    out['historical_region']=summary([r for r in old if r['member'] in REGION])
    (ROOT/'results/summary.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'data/regional_2025.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(region)
    print(json.dumps(out,indent=2))
