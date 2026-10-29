"""Parameterized calculation, not a datasheet claim or bench result."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.benchmark import loss_model
p=argparse.ArgumentParser(description=__doc__)
for key in ['vin','vout','iout','frequency','high-r','low-r','diode-v','dcr','rise-fall-ns']:
    p.add_argument('--'+key,required=True,type=float)
p.add_argument('--synchronous',action='store_true')
a=p.parse_args()
try: r=loss_model(a.vin,a.vout,a.iout,a.frequency,a.high_r,a.low_r,a.diode_v,a.dcr,a.rise_fall_ns,a.synchronous)
except ValueError as e:p.error(str(e))
print(json.dumps(r,indent=2,allow_nan=False))
