import math
from pathlib import Path
import tempfile
import unittest
from src.benchmark import Measurement,loss_model,load,summarize,svg

class BenchmarkTests(unittest.TestCase):
    def test_known_efficiency_and_thermal_rise(self):
        r=Measurement('unit','one',12,.5,5,1,25,40,1).result()
        self.assertAlmostEqual(r['efficiency_pct'],100*5/6)
        self.assertEqual(r['loss_w'],1);self.assertEqual(r['case_rise_c'],15)
    def test_invalid_measurements(self):
        for iin in [0,-1,float('nan'),.1]:
            with self.assertRaises(ValueError): Measurement('unit','one',12,iin,5,1,25,40).result()
    def test_analytical_losses(self):
        r=loss_model(12,5,3,180000,.06,.1,.5,.02,40,False)
        self.assertAlmostEqual(r['freewheel_w'],.875)
        self.assertEqual(r['kind'],'analytical_estimate_not_measurement')
    def test_operating_points_are_separate(self):
        a=Measurement('A','1',12,.5,5,1,25,30).result()
        b=Measurement('A','2',12,1,5,2,25,30).result()
        self.assertEqual(len(summarize([a,b])),2)
    def test_missing_data_rejected(self):
        with self.assertRaises(ValueError): load('experiments/measurement-template.csv')
    def test_duplicate_runs_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv'
            p.write_text('converter,run_id,vin_v,iin_a,vout_v,iout_a,ambient_c,case_c,uncertainty_pct\nA,1,12,0.5,5,1,25,40,1\nA,1,12,0.5,5,1,25,40,1\n')
            with self.assertRaises(ValueError):load(p)
    def test_plot_escapes_identifiers(self):
        r=Measurement('<unsafe>','1',12,.5,5,1,25,40).result()
        self.assertIn('&lt;unsafe&gt;',svg([r]))
        self.assertNotIn('<unsafe>',svg([r]))
if __name__=='__main__':unittest.main()
