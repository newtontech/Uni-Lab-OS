# Minimal Workflow

This page captures the smallest workflow a new lab should verify before connecting production equipment.

## Goal

Run a recipe through Uni-Lab-OS, exchange messages through `unilabos_msgs`, and produce a reviewed run log with either a mocked device or a safe simulator.

## Steps

1. Create the recommended conda/mamba environment.
2. Install `unilabos` or install the repository in editable mode for development.
3. Pick one boot example from the official documentation.
4. Run it with a mocked device or simulator.
5. Save the run log and configuration.
6. Add one real device only after the mocked path is stable.

## Device onboarding checklist

- Device model and firmware version are documented.
- Connection type is documented.
- Safe startup and shutdown states are documented.
- Required calibration or warm-up steps are documented.
- Failure behavior is documented before unattended runs.
