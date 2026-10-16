"""Extract factual register cells; never infer jurisdiction from policy ownership."""
from pathlib import Path
import argparse, csv, hashlib, json, re, subprocess
import fitz

FIELDS = ['row','member','project','sector','financing_type','lead','usd_million','approval','es_reference','policy','iam']

def extract(pdf):
    result = []
    for page_no, page in enumerate(fitz.open(pdf), 1):
        for table in page.find_tables().tables:
            for cells in table.extract():
                if not cells[0] or not cells[0].strip().isdigit():
                    continue
                assert len(cells) == 11, (page_no, cells)
                values = [' '.join((x or '').split()) for x in cells]
                row = dict(zip(FIELDS, values))
                row['row'] = int(row['row'])
                row['usd_million'] = row['usd_million'].replace('$','').replace(',','')
                row['source_page'] = page_no
                row['source_sha256'] = hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
                result.append(row)
    return sorted(result, key=lambda x:x['row'])

def verify_poppler(pdf, rows):
    """Independent text engine and regex verify critical cells on all rows."""
    text = subprocess.check_output(['pdftotext','-layout',str(pdf),'-'], text=True)
    for r in rows:
        lines = [s for s in text.splitlines() if re.match(r'^\s*'+str(r['row'])+r'\s',s)]
        assert len(lines) == 1, (r['row'],lines)
        line = lines[0]
        amount = re.search(r'\$([\d,]+\.\d{2})',line)
        assert amount and amount[1].replace(',','') == r['usd_million']
        assert r['approval'] in line
        # All applicable-policy and IAM cells fit on the numbered line.
        tail = re.split(r'\d{1,2}-[A-Za-z]{3}-\d{2}',line)[-1]
        assert tail.split() == (r['es_reference']+' '+r['policy']+' '+r['iam']).split(),(r,tail)
    return len(rows)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    parser.add_argument('csv',type=Path)
    parser.add_argument('--expected',type=int,required=True)
    args=parser.parse_args()
    rows=extract(args.pdf)
    assert [r['row'] for r in rows] == list(range(1,args.expected+1))
    checked=verify_poppler(args.pdf,rows)
    args.csv.parent.mkdir(parents=True,exist_ok=True)
    with args.csv.open('w') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS+['source_page','source_sha256'])
        w.writeheader();w.writerows(rows)
    print(json.dumps({'extracted':len(rows),'independent_critical_cell_checks':checked,'sha256':rows[0]['source_sha256']}))
