# Big Spool

**Date:** 2025-07-01
**Setup:** Large-spool drive configuration with cogging-torque compensation.

Torque characterization of the larger spool. The script that produced these plots is
archived at [`../../Tests/trq_test_big_spool.py`](../../Tests/trq_test_big_spool.py);
it ramps feedforward torque up and back down (triangle profile) while logging motor
telemetry and load cell output.

## Files

- `torque_test.png` — full torque ramp.
- `torque_test_5sec.png` — shorter 5-second ramp.
- `torque_test_no_spring.png` — ramp with the return spring removed.
