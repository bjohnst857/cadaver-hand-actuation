# Cogging-Torque Compensation

**Date:** 2025-05-17
**Setup:** Cogging-torque compensation applied in software.

Repeat of the baseline tests ([`../no_compensation/`](../no_compensation/)) with the
moteus cogging-torque compensation enabled.

## Files

- `torque_test.png` — torque test results.
- `velocity_test.png` — velocity test results.
- `position_test.png` — position test results.

## Compensation procedure

moteus cogging-torque compensation docs:
<https://docs.google.com/document/d/1M4O-LVki03qonNTkydv1N8gRteGIZk3ZyHd-mBpxL-U/edit>

Steps (per Josh Pieper, moteus Discord):

1. Flash firmware `2025-04-30`.
2. `conf default`
3. Set `servopos.position_min` and `servopos.position_max` to `nan`.
4. `moteus_tool -t 1 --calibrate`
5. `./utils/compensate_encoder.py --plot`
6. `moteus_tool -t 1 --calibrate`
7. `utils/compensate_cogging.py --store --plot-results`
