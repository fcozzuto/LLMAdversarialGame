# Phase 5 TSP Benchmarks

This directory contains the benchmark pack for the replay-aware TSP phase.

## Contents

- [manifest.json](manifest.json): main phase-5 benchmark manifest
- [smoke_manifest.json](smoke_manifest.json): smaller smoke-test subset
- `tsplib95/`: downloaded TSPLIB95 problem files and optimal-tour files for the selected EUC_2D subset

## Source Basis

- Official catalog: [TSPLIB95 TSP data](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp.html)
- Official best-known symmetric tour values: [STSP best-known solutions](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/STSP.html)
- Direct file retrieval in the preparation script currently uses the Rice mirror: [softlib.rice.edu/pub/tsplib/tsp](http://softlib.rice.edu/pub/tsplib/tsp/)

The benchmark-preparation script computes `best_known_cost` values from the corresponding optimal-tour files for the selected subset instead of hardcoding them by hand.

## Preparation

```powershell
python prepare_tsp_benchmarks.py
```
