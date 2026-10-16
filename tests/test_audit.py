import unittest, csv, json, itertools, sys
from pathlib import Path
from datetime import date
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import ROOT, REGION, policy_error, route, summary, read_csv
from ledger import lookup

class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_csv(ROOT/'data/register_2025.csv')
        cls.events=json.loads((ROOT/'data/shokpar_events.json').read_text())

    def test_row_integrity(self):
        self.assertEqual([int(r['row']) for r in self.rows],list(range(1,153)))
        self.assertTrue(all(len(r['source_sha256'])==64 for r in self.rows))

    def test_visually_checked_regional_cells(self):
        gold=read_csv(ROOT/'data/regional_check.csv')
        actual=[{k:r[k] for k in gold[0]} for r in self.rows if r['member'] in REGION]
        self.assertEqual(actual,gold)

    def test_aggregation_exact_decimal(self):
        r=[r for r in self.rows if r['member'] in REGION]
        self.assertEqual(summary(r)['usd_million'],'5417.78')
        self.assertEqual(summary(r)['ppm_usd_million'],'677.50')
        self.assertEqual(summary(r)['delegated_rows'],23)

    def test_policy_error_with_exhaustive_lookup_oracle(self):
        policies=sorted({r['policy'] for r in self.rows})
        choices=[sorted({r['iam'] for r in self.rows if r['policy']==p}) for p in policies]
        errors=[]; weighted=[]
        for labels in itertools.product(*choices):
            rule=dict(zip(policies,labels))
            errors.append(sum(rule[r['policy']]!=r['iam'] for r in self.rows))
            weighted.append(sum((Decimal(r['usd_million']) for r in self.rows if rule[r['policy']]!=r['iam']),Decimal(0)))
        self.assertEqual(min(errors),14)
        self.assertEqual(min(errors),policy_error(self.rows))
        self.assertEqual(min(weighted),Decimal('1162.70'))
        self.assertEqual(min(weighted),policy_error(self.rows,True))

    def test_policy_borrowing_is_not_forum_delegation(self):
        a,b=lookup(57),lookup(67)
        self.assertEqual(a['policy_label'],b['policy_label'])
        self.assertNotEqual(a['iam'],b['iam'])

    def test_source_required_and_missing_not_denial(self):
        self.assertEqual(route({'policy':'EBRD ESP'})['status'],'unresolved')
        self.assertEqual(route({'iam':'EBRD IPAM'})['status'],'unresolved')
        self.assertEqual(lookup(1000)['status'],'unresolved')

    def test_lead_does_not_determine_policy(self):
        r=next(r for r in self.rows if r['row']=='151')
        self.assertEqual((r['lead'],r['policy'],r['iam']),('WB-led','AIIB ESP','AIIB PPM'))

    def test_snapshot_join_has_no_routing_change(self):
        old=read_csv(ROOT/'data/register_2024.csv')
        key=lambda r:(r['member'],r['approval'],r['usd_million'],r['project'])
        new={key(r):r for r in self.rows}
        for r in old:
            self.assertIn(key(r),new)
            self.assertEqual((r['policy'],r['iam']),(new[key(r)]['policy'],new[key(r)]['iam']))

    def test_month_only_events_retain_uncertainty(self):
        e=next(e for e in self.events if e['id']=='reports')
        self.assertEqual((e['date_low'],e['date_high']),('2026-01-01','2026-01-31'))
        self.assertNotEqual(e['date_low'],e['date_high'])

    def test_intake_referral_registration_intervals(self):
        dates={e['id']:date.fromisoformat(e['date_low']) for e in self.events}
        self.assertEqual((dates['referral']-dates['intake']).days,16)
        self.assertEqual((dates['registration']-dates['intake']).days,162)
        self.assertEqual((dates['registration']-dates['suspension']).days,97)

    def test_delivery_does_not_mean_equal_access(self):
        e=next(e for e in self.events if e['id']=='reports')
        self.assertEqual(e['reports'],4)
        self.assertNotIn('Requesters',e['full_report_recipients'])
        self.assertEqual(e['requester_access'],'summaries_only')

    def test_stage_closure_not_case_closure(self):
        last=self.events[-1]
        self.assertEqual(last['kind'],'status_snapshot')
        self.assertIn('case open',last['event'])
        self.assertIn('no agreement',self.events[-2]['event'])

if __name__=='__main__':unittest.main()
