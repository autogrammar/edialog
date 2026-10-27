# Ticket 001: Reconcile dockuri SSoT manifests, register standard dependencies, and deduplicate internal clones

- **ID**: ticket-001
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-27

SESSION_EXECUTION_AUTHORIZATION: user requested auditing standard dependencies, SSoT duplication, and `semcod/redup` detection across `wellmanifest/*`, then remediating all anomalies in pilot project `autogrammar/edialog` before fleet rollout.

## Goal and scope

1. Synchronize canonical URI definitions and version `0.4.5` across `dockuri.json`, `dockuri.yaml`, and `uriprocess.json` (12 canonical URIs).
2. Deduplicate internal clone groups in `src/edialog/models.py`, `src/edialog/cli.py`, `src/edialog/fiction_cli.py`, `src/edialog/nl.py`, `src/edialog/backends.py`, `src/edialog/fiction.py`, and `src/edialog/vision.py` so `redup scan src` reports 0 duplicate groups.
3. Register complete `baseline` + `domain-pack` + runtime/domain standards and their transitive `requires` dependencies in `.governance/standard-requirements.json` and `.governance/standard-packs.json`.
4. Generate `.planfile/sprints/current.yaml` and `.reuse/redup-receipt.json` to satisfy `wellmanifest/reuse` conformance (`REUSE-002`, `REUSE-004`, `REUSE-006A`, `REUSE-006B`).

## Acceptance criteria

- [x] AC-01: `dockuri.json`, `dockuri.yaml`, and `uriprocess.json` expose the exact same 12 canonical `proc://edialog/...` URIs at version `0.4.5`.
- [x] AC-02: `redup scan src` reports 0 duplicate groups and `wellmanifest/reuse` conformance passes (`REUSE-002`, `REUSE-004`, `REUSE-006A`, `REUSE-006B`).
- [x] AC-03: `.governance/standard-requirements.json` and `.governance/manifest.lock.json` pass `./project/governance-check.sh` and `wellman check` with 0 errors.
- [x] AC-04: All 168 unit tests pass.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
