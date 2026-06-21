# Motor Testing Results

Saved plots, CSV logs, and notes from the motor characterization experiments. Each
subfolder is one experiment and has its own `README.md` describing the setup. The
test scripts that produced these results live in [`../Tests`](../Tests).

| Experiment | Date | Setup | Contents |
|---|---|---|---|
| [`no_compensation/`](no_compensation/) | 2025-05-12 | Small spool, S-type load cell, **no** cogging-torque compensation | torque, velocity |
| [`cogging_compensation/`](cogging_compensation/) | 2025-05-17 | Software cogging-torque compensation enabled | torque, velocity, position |
| [`big_spool/`](big_spool/) | 2025-07-01 | Large-spool drive configuration | torque (full, 5 s, no-spring) |
| [`load_cell_comparison/`](load_cell_comparison/) | 2025-07-01 | Big spool + compensation; inline vs. S-type load cell | torque, repeat runs, range sweeps |

## File conventions

- `torque_test.png` / `velocity_test.png` / `position_test.png` — result plots.
- `*_data.csv` — raw logs with columns: `times, trqs, cmd_trqs, s_ratios, j_ratios`
  (time s, measured torque, commanded torque, S-type ratio, inline ratio).
