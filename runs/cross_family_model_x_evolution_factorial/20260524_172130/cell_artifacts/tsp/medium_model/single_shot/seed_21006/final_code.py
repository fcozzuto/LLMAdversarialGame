def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (single_shot, Candidate 1)
    # Notes:
    # - No imports
    # - Return a dictionary with interpretable fields
    # - Focus on robustness for held-out TSPLIB-like instances and synthetic transfers
    # - Simple, deterministic logic encoded in the scaffold

    heuristic = {
        "name": "constrained_tsp_single_shot_scaffold",
        "version": 1,
        "description": "Deterministic, interpretable scaffold for constrained TSP heuristic",
        "assumptions": [
            "Asymmetric or symmetric distances are provided by the environment as a distance matrix",
            "There is a fixed set of mandatory nodes to visit (or a fixed order constraint) encoded as 'must_visit' subset",
            "Maximum allowed tour length or city count constraint may be provided via environment; if not, defaults apply",
            "No external randomness; deterministic tie-breaking via node indices"
        ],
        "data_requirements": {
            "distance_matrix": "2D square matrix of non-negative distances; indexable by node id",
            "nodes": "List of node identifiers corresponding to distance_matrix indices",
            "constraints": {
                "must_visit": "Optional set or list of node ids that must be included in the tour",
                "forbidden": "Optional set or list of node ids that must be avoided (if present)"
            },
            "start_node": "Optional start node id; if None, 0 is used",
            "end_node": "Optional end node id; if None, tour ends at start_node or after visiting all required nodes"
        },
        "strategy": {
            "phase": "single_shot construction; do not iterate or replan after initial pass",
            "ordering": "Deterministic nearest-eligible insertion with fixed tie-breaking by index",
            "insertion_policy": "Maintain constraints; prefer nodes that minimally extend current path length while respecting constraints",
            "duration_cap": "If provided as numeric, cap the computed tour length; otherwise no explicit cap",
            "feasibility_check": true
        },
        "construction": {
            "initial_order": "Sorted list of nodes by index to ensure determinism",
            "must_visit_first": True,
            "path_building": [
                "Start at start_node if provided, else smallest index",
                "Iteratively insert the next eligible node (not yet visited, not forbidden) that minimally increases total distance",
                "Whenever a node becomes ineligible due to constraints, skip with deterministic rule",
                "Finish when all must_visit nodes are included; optional end_node handling",
            ],
            "end_condition": "All must_visit nodes are included; if end_node specified, ensure path ends there if feasible",
            "latency_model": "Not modeled; deterministic computation time proportional to n^2 for small n"
        },
        "robustness": {
            "transfer_friendly": True,
            "avoid_overfitting": True,
            "fallbacks": [
                "If no feasible path found under constraints, return a minimal feasibility path visiting must_visit in index order",
                "If end_node unavailable, return path ending at last visited node"
            ]
        },
        "outputs": {
            "tour": "List of node ids in visiting order (including repeated start if needed to close tour depending on convention)",
            "tour_length": "Total distance of the computed tour using distance_matrix",
            "feasible": "Boolean flag indicating if all must_visit and constraints are satisfied",
            "log": "Optional deterministic trace as list of strings for debugging (not required by consumer)"
        },
        "deterministic": True,
        "compatibility": {
            "tsp_formats": ["distance matrix", "node list with constraints"],
            "expected_environment": "scaffold used by constrained_tsp evaluators",
        },
        "notes": [
            "This scaffold avoids randomness and imports.",
            "It provides a transparent heuristic that can be replaced with a more advanced planner by swapping the implementation details while preserving the dictionary schema.",
            "The structure is intentionally minimal to be robust across TSPLIB-like and synthetic instances."
        ]
    }

    return heuristic
