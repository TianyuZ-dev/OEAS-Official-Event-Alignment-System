# FrictionGraph Processed Exports

This public upload does not include the full FrictionGraph processed export files.

To run alignment locally, place the following FrictionGraph CSV exports here or pass explicit paths to `run_alignment.py`:

```text
daily_width_features_all.csv
chain_day_features_all.csv
```

Example:

```bash
python3 run_alignment.py \
  --exposures output/events_jpy_stress/accepted_exposures_latest.json \
  --friction-daily data/frictiongraph/daily_width_features_all.csv \
  --friction-chain data/frictiongraph/chain_day_features_all.csv \
  --output-dir output/alignment_jpy_stress \
  --ranking-mode relevance
```

Small derived Tableau CSVs are included under `output/tableau_*` so reviewers can inspect the portfolio outputs without the private FrictionGraph data lake.

