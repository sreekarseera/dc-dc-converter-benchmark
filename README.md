# DC-DC Converter Benchmark

New Python tools for reducing measured XL4015/MP2307 (or other converter)
load-test data. This is an analysis tool, not firmware for an invented controller.
The owner supplied a converter comparison report; original analysis code and
machine-readable measurements were not located. This implementation was prepared
on 29 October 2026 and has no claimed earlier development history.

## Run

Python 3.11+; no packages required:

    python3 -m unittest discover -s tests -v
    python3 src/benchmark.py my-measurements.csv --output output
    python3 tools/model_losses.py --vin 12 --vout 5 --iout 3 --frequency 180000 --high-r 0.06 --low-r 0.1 --diode-v 0.5 --dcr 0.02 --rise-fall-ns 40

The last command uses illustrative, user-specified assumptions; it produces an
analytical estimate, not a measured XL4015 specification. Change parameters to
match verified component data and operating conditions.

Copy experiments/measurement-template.csv and enter actual readings. The tool
rejects empty/non-finite/impossible input, produces JSON efficiency/loss/thermal
rise and an SVG plot, and groups repeated readings only at matching operating
points. No experimental results ship with the repository. The uncertainty column
is recorded as supplied; combined uncertainty is not calculated or certified.

See docs/methodology.md and docs/attribution.md.
