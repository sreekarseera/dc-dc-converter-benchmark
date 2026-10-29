# Measurement protocol and interpretation

Use a current-limited low-voltage supply, correctly rated converter, electronic
load and suitable instruments. Confirm polarity and load power ratings first.
Measure Vin/Iin at the converter input and Vout/Iout at its output; measure lead
loss separately. Keep input voltage/output setpoint, airflow, ambient conditions
and stabilization criteria consistent across modules. Do not compare one module
at 5V output to another at 3.3V as if it were a controlled comparison.

For each point assign a unique run_id, record converter revision, instruments,
ambient and case temperature, actual terminal readings, settling time and limits.
Repeat each operating point. Use the same contact/IR temperature method and
emissivity assumptions; case temperature does not equal junction temperature.

Pin=Vin*Iin, Pout=Vout*Iout, efficiency=100*Pout/Pin, loss=Pin-Pout.
Case rise=case temperature minus ambient temperature. A measured efficiency over
100% is rejected rather than silently clamped. Investigate measurement alignment,
resolution and wiring. Store raw data and instrument uncertainty alongside results.

The optional loss model assumes CCM and ideal duty Vout/Vin. It omits quiescent,
gate-drive, core, temperature-dependent and other losses. It is not a substitute
for load tests, switching-waveform captures or measured thermal behavior.
