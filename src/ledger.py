"""Evidence-carrying lookup, not an automatic complaint-eligibility decision."""
import argparse, csv, json
from pathlib import Path
from analyze import ROOT, route, read_csv

def lookup(row, snapshot='2025'):
    records=read_csv(ROOT/f'data/register_{snapshot}.csv')
    matches=[r for r in records if r['row']==str(row)]
    if len(matches)!=1:
        return {'status':'unresolved','reason':'No unique record in this snapshot'}
    r=matches[0]
    r['source_locator']=f"end-{snapshot} register, PDF page {r['source_page']}, row {r['row']}"
    return dict(route(r),project=r['project'],policy_label=r['policy'],
       source_locator=r['source_locator'],sha256=r['source_sha256'],snapshot=f'end-{snapshot}',
       scope='AIIB-designated IAM only; this is not a list of all co-financier or domestic remedies',
       eligibility='Not adjudicated; requires applicable dates, standing, issue and mechanism rules')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--row',type=int,required=True)
    p.add_argument('--snapshot',choices=['2024','2025'],default='2025')
    a=p.parse_args();print(json.dumps(lookup(a.row,a.snapshot),indent=2))
