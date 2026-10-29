"""DC-DC measurement reduction. Inputs must be real measured terminal quantities."""
import argparse
import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
import html
import json
import math
from pathlib import Path
import statistics

@dataclass
class Measurement:
    converter: str
    run_id: str
    vin_v: float
    iin_a: float
    vout_v: float
    iout_a: float
    ambient_c: float
    case_c: float
    uncertainty_pct: float = 0.0

    def result(self):
        numeric=[self.vin_v,self.iin_a,self.vout_v,self.iout_a,self.ambient_c,self.case_c,self.uncertainty_pct]
        if not all(math.isfinite(v) for v in numeric): raise ValueError('Non-finite measurement')
        if not self.converter.strip() or not self.run_id.strip(): raise ValueError('Missing converter/run identifier')
        if self.vin_v<=0 or self.iin_a<=0 or self.vout_v<0 or self.iout_a<0:
            raise ValueError('Input power must be positive and output quantities nonnegative')
        if not 0<=self.uncertainty_pct<=100:raise ValueError('Uncertainty must be between 0 and 100 percent')
        pin=self.vin_v*self.iin_a; pout=self.vout_v*self.iout_a
        efficiency=100*pout/pin
        if efficiency>100:raise ValueError('Output exceeds input: check instrument range, simultaneous readings, wiring')
        return {**asdict(self),'pin_w':pin,'pout_w':pout,'loss_w':pin-pout,
                'efficiency_pct':efficiency,'case_rise_c':self.case_c-self.ambient_c}


def load(path):
    rows=[]
    with open(path,newline='') as f:
        for n,row in enumerate(csv.DictReader(f),2):
            try:
                m=Measurement(**{k:row[k] if k in ('converter','run_id') else float(row[k])
                                  for k in Measurement.__dataclass_fields__})
                rows.append(m.result())
            except (ValueError,KeyError,TypeError) as e:raise ValueError(f'CSV line {n}: {e}') from e
    if not rows:raise ValueError('No measurement rows supplied')
    identifiers=[(r['converter'],r['run_id']) for r in rows]
    if len(set(identifiers))!=len(identifiers):raise ValueError('Duplicate converter/run_id; assign each measurement a unique run_id')
    return rows


def summarize(rows):
    groups=defaultdict(list)
    for row in rows:
        # Never combine different voltage or load operating points into one efficiency average.
        groups[(row['converter'],row['vin_v'],row['vout_v'],row['iout_a'])].append(row)
    return [dict(converter=key[0],vin_v=key[1],vout_v=key[2],iout_a=key[3],
                 repetitions=len(values),mean_efficiency_pct=statistics.mean(v['efficiency_pct'] for v in values),
                 stdev_efficiency_pct=statistics.stdev(v['efficiency_pct'] for v in values) if len(values)>1 else None)
            for key,values in sorted(groups.items())]


def loss_model(vin,vout,iout,frequency,high_r,low_r,diode_v,dcr,rise_fall_ns,synchronous):
    vals=[vin,vout,iout,frequency,high_r,low_r,diode_v,dcr,rise_fall_ns]
    if not all(math.isfinite(v) for v in vals) or not 0<vout<vin or iout<0 or frequency<=0 or min(vals[4:])<0:
        raise ValueError('Invalid model parameters; this model assumes step-down CCM operation')
    duty=vout/vin
    losses={'high_side_w':iout*iout*high_r*duty,
            'freewheel_w':iout*iout*low_r*(1-duty) if synchronous else iout*diode_v*(1-duty),
            'switching_w':.5*vin*iout*rise_fall_ns*1e-9*frequency,
            'inductor_w':iout*iout*dcr}
    total=sum(losses.values());pout=vout*iout
    return {'kind':'analytical_estimate_not_measurement','duty':duty,**losses,
            'modeled_loss_w':total,'modeled_efficiency_pct':100*pout/(pout+total) if pout+total>0 else None,
            'omissions':['quiescent current','gate drive','core losses','capacitor ESR','temperature dependence','DCM/light-load control']}


def svg(rows):
    # Group at the same supply/output voltage, so curves have a defined operating condition.
    groups=defaultdict(list)
    for r in rows:groups[(r['converter'],r['vin_v'],r['vout_v'])].append(r)
    xmax=max(r['iout_a'] for r in rows) or 1
    height=max(560,500+20*len(groups))
    text=[f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}">',
          '<rect width="100%" height="100%" fill="white"/>',
          '<text x="60" y="28" font-family="sans-serif" font-size="18">Measured conversion efficiency</text>',
          '<path d="M60 50 V410 H860" fill="none" stroke="#444"/>',
          '<text x="350" y="447" font-family="sans-serif">Output current (A)</text>',
          '<text x="10" y="45" font-family="sans-serif">%</text>']
    colors=['#006d77','#b7440e','#6247aa','#297045']
    for p in range(0,101,20):
        y=410-p*3.4
        text.append(f'<text x="20" y="{y}" font-size="12">{p}</text><path d="M60 {y} H860" stroke="#ddd"/>')
    for tick in range(6):
        current=xmax*tick/5;x=60+780*tick/5
        text.append(f'<text x="{x}" y="429" font-size="12">{current:.2f}</text>')
    for idx,(key,values) in enumerate(sorted(groups.items())):
        color=colors[idx%len(colors)]
        # Points only: interpolation across operating points is not a physical measurement.
        for v in values:
            x=60+780*v['iout_a']/xmax;y=410-3.4*v['efficiency_pct']
            text.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"/>')
        label=html.escape(f'{key[0]}: Vin={key[1]:g}V, Vout={key[2]:g}V')
        text.append(f'<text x="60" y="{475+idx*20}" fill="{color}" font-family="sans-serif">{label}</text>')
    text.append('</svg>');return '\n'.join(text)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv');p.add_argument('--output',default='output')
    a=p.parse_args()
    try:rows=load(a.csv)
    except (ValueError,OSError) as e:p.error(str(e))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/'results.json').write_text(json.dumps({'measurements':rows,'summary':summarize(rows)},indent=2,allow_nan=False)+'\n')
    (out/'efficiency.svg').write_text(svg(rows))
    print(f'Analyzed {len(rows)} rows; wrote {out}/results.json and efficiency.svg')

if __name__=='__main__': main()
