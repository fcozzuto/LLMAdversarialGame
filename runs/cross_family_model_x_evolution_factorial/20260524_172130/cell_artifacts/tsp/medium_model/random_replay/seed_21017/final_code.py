def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for constrained TSP heuristic using robust, interpretable components with a random_replay technique placeholder.",
        "technique": "random_replay",
        "strategy": {
            "assumptions": [
                "Locations have fixed coordinates and indexable identifiers.",
                "Constraints include required mandatory visits, and optional constraints like time windows (if provided).",
                "All decisions must be deterministic given the same input seed and data.",
            ],
            "components": [
                {
                    "name": "initial_seed_selection",
                    "purpose": "Choose a deterministic starting node based on a stable property (e.g., smallest id).",
                    "logic": "start_node = min(nodes, key=lambda n: n['id'])",
                    "notes": "No randomness; purely deterministic."
                },
                {
                    "name": "nearest_feasible_next",
                    "purpose": "Greedily extend the tour by the nearest feasible city that respects constraints and feasibility.",
                    "logic": (
                        "for candidate in sorted(remaining_nodes, key=lambda n: distance(last, n)):\n"
                        "    if is_feasible(next_node=candidate, tour=tour, constraints=constraints):\n"
                        "        return candidate\n"
                        "return None"
                    ),
                    "notes": "Deterministic tie-breaker via sorted order."
                },
                {
                    "name": "feasibility_checker",
                    "purpose": "Assess whether appending a candidate keeps constraints satisfiable.",
                    "logic": "return True if constraints_are_satisfied_after_append(tour, candidate, constraints) else False",
                    "notes": "Keeps the search robust under constraints."
                },
                {
                    "name": "violations_trimmer",
                    "purpose": "If no feasible next exists, backtrack to last feasible prefix within a small cutoff to ensure progress.",
                    "logic": "truncate_tour_to_last_feasible_prefix(tour, constraints)",
                    "notes": "Limited backtracking to keep interpretability."
                },
                {
                    "name": "quality_estimator",
                    "purpose": "Provide a deterministic score for a partial tour to aid interpretation.",
                    "logic": "score = -sum(distance(tour[i], tour[i+1]) for i in range(len(tour)-1))",
                    "notes": "Lower score indicates shorter path; simple and transparent."
                },
                {
                    "name": "random_replay_placeholder",
                    "purpose": "Deterministic replay surface for extensibility; uses fixed, precomputed replay log when available.",
                    "logic": "replay_log = []  # empty by default; deterministic path if populated externally",
                    "notes": "No replay entries available yet; scaffold in place."
                }
            ],
            "data_model": {
                "nodes_key": "nodes",  # each node: {'id': int, 'coords': (x, y), ...}
                "constraints_key": "constraints",  # e.g., {'mandatory': {ids}, 'max_length': int, ...}
                "tour_key": "tour"  # list of node ids in visit order
            }
        },
        "tuning": {
            "seed": 42,
            "replay_seed": 0,
            "parameters": {
                "backtracking_cutoff": 2,
                "neighbor_order": "sorted_by_distance",
                "tie_breaker": "by_id"
            }
            ,
            "robustness": {
                "test_sources": ["TSPLIBs", "synthetic_transfer_sets"],
                "transfer_robustness": "moderate"
            }
            ,
            "interpretability": "high"
        },
        "notes": [
            "This is a deterministic scaffold; no imports or external dependencies.",
            "Ready to be bound to a concrete distance function and feasibility checks in the caller context.",
            "Candidate 1: no replay archive entries are available yet."
        ]
    }
