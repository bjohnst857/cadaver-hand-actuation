# Load Cell Comparison

**Date:** 2025-07-01 (repeat runs 2025-07-02)
**Setup:** Big spool with cogging-torque compensation.

Tests designed to compare the **inline** load cell against the **S-type** load cell.
The data logs the two side by side: `s_ratios` is the S-type reading and `j_ratios`
is the inline reading. The script is
[`../../Tests/trq_test_for_load_cell_compare.py`](../../Tests/trq_test_for_load_cell_compare.py).

## Files

- `torque_test.png` / `torque_test_data.csv` — primary comparison run.

### Subfolders

- `repeat_runs/` — three repeat trials on 2025-07-02 (`run_<HH-MM>_data.csv` +
  `run_<HH-MM>_plot.png`) for run-to-run repeatability.
- `no_inline/` — run with the inline load cell removed (S-type only).
- `up_to_0.4Nm/` — torque sweep limited to 0.4 N·m.
- `up_to_0.7Nm/` — torque sweep limited to 0.7 N·m.

## CSV columns

`times, trqs, cmd_trqs, s_ratios, j_ratios` — time (s), measured torque, commanded
torque, S-type load cell ratio, inline load cell ratio.
