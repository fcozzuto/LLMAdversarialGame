def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a "random_replay" style outline.
    # Note: No external imports. This scaffold favors interpretability with robust, transferable design.
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "technique": "random_replay",
        "description": (
            "Deterministic scaffold for a constrained TSP heuristic. "
            "Uses simple, interpretable steps with deterministic choices to allow robust transfer "
            "to held-out TSPLIB and synthetic instances."
        ),
        "assumptions": [
            "Graph is a complete symmetric distance matrix preprocessed into coordinates if available.",
            "Constraints are provided as per-instance feasible sets (e.g., mandatory nodes, forbidden edges).",
            "Tour must satisfy all hard constraints; soft constraints influence scoring if present.",
        ],
        "data_sources": {
            "training": ["synthetic instances generated with moderate size and constraint variety"],
            "held_out": ["TSPLIB-like instances with standard benchmarks (e.g., tsplib95 style)"],
            "transfer": ["synthetic transfer instances with varied density and constraint patterns"],
        },
        "components": [
            {
                "phase": "initialization",
                "description": "Create a deterministic starting tour by a simple nearest-eligible-unvisited heuristic with constraint checks.",
                "deterministic_seed": 42,
                "steps": [
                    "order_of_nodes = sorted(nodes, key=lambda i: i)  # deterministic by index",
                    "current = order_of_nodes[0]",
                    "visited = {current}",
                    "tour = [current]",
                ],
            },
            {
                "phase": "construction",
                "description": "Greedily extend tour by selecting the closest feasible next node that respects constraints.",
                "methods": [
                    "for each step, compute candidates not in visited",
                    "filter candidates by feasibility with constraints (e.g., mandatory/forbidden edges, max degree)",
                    "choose candidate with minimum distance to current; tie-break deterministically by node index",
                    "append to tour; mark visited",
                ],
            },
            {
                "phase": "closure",
                "description": "Close the tour by returning to the start if feasible; otherwise attempt a simple swap-based repair.",
                "strategies": [
                    "prefer direct return if edge feasible",
                    "else perform one-swap repair to connect end to start while maintaining feasibility",
                ],
            },
            {
                "phase": "feasibility",
                "description": "Ensure all hard constraints are satisfied; if not, apply a minimal penalty path to repair.",
                "penalties": [
                    "unvisited mandatory nodes incur high cost to trigger repair",
                    "forbidden edges incur infinite cost in scoring (not chosen)"
                ],
            },
            {
                "phase": "scoring",
                "description": "Compute tour length with simple exact distance sum; optional soft-constraint penalties applied with fixed weights.",
                "parameters": {
                    "distance_weight": 1.0,
                    "soft_constraint_penalty": 0.0,  # kept simple for interpretability
                },
            },
        ],
        "outputs": {
            "tour": "list[int] representing ordered node indices forming a feasible tour",
            "feasibility_flags": "dict mapping constraint checks to booleans",
            "score": "float total tour length",
        },
        "constraints_handling": {
            "hard": [
                "visit each node exactly once",
                "respect mandatory edges (if any)",
                "avoid forbidden edges (if any)"
            ],
            "soft": [
                "minimize total distance",
                "prefer fewer constraint violations if soft penalties present"
            ],
        },
        "robustness_considerations": [
            "deterministic behavior for reproducibility",
            "works for moderate-sized instances common in TSPLIB and synthetic benchmarks",
            "transparent heuristic steps for auditing and extension"
        ],
        "notes": [
            "This scaffold is intentionally lightweight and interpretable; it is not a full solver.",
            "To implement, replace with concrete distance computations and constraint data structures in the consuming code."
        ],
        "metadata": {
            "authors": ["random_replay_candidate_1"],
            "replay_archived_entries": [],
            "seed": 42
        }
    }
