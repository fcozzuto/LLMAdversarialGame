def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "technique": "failure_replay_compression",
        "parameters": {
            "replay_archive": [],
            "compression_threshold": 0.05,
            "max_compression_iterations": 5,
            "use_heuristic_reduction": True,
            "min_edge_cost": 1e-6
        },
        "heuristic": [
            "Construct an initial tour using a nearest neighbor heuristic.",
            "Identify edges that are consistently avoided or cause failures.",
            "Compress the tour by replacing sequences of edges with shortcut edges if their total cost exceeds a threshold.",
            "Maintain and update a replay archive with failed attempts for future guidance.",
            "Iteratively refine the tour by attempting recovery with stored failure patterns, applying compression only if it improves robustness.",
            "Terminate when no further improvements are seen or maximum iterations achieved."
        ],
        "robustness": "Prioritizes robustness across TSPLIB and synthetic datasets, utilizing failure patterns to guide compression and improve solution stability.",
        "interpretability": "Uses straightforward heuristics like nearest neighbor and simple compression thresholds, with a transparent failure replay mechanism."
    }

