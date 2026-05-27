def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "description": "Deterministic, interpretable constrained TSP heuristic scaffold with failure_replay_compression approach groundwork.",
        "version": "1.0",
        "technique": "failure_replay_compression",
        "assumptions": [
            "Constrained TSP: each city must be visited exactly once, subject to side constraints (e.g., precedence, optionality, or resource limits).",
            "No external replay archives available yet; deterministic fallback behavior is used.",
            "Heuristic aims to be robust across TSPLIB-like and synthetic transfer instances.",
            "Interpretability prioritized over excessive optimization."
        ],
        "components": [
            {
                "id": "feasibility_check",
                "purpose": "Verify constraint satisfaction for a partial or complete tour.",
                "method": "linear/simple rule checks with deterministic ordering; does not rely on randomness."
            },
            {
                "id": "priority_order",
                "purpose": "Provide a stable, explainable city ordering baseline to guide construction.",
                "method": "static tie-breaking based on city index and constraint-derived priorities."
            },
            {
                "id": "greedy_extend",
                "purpose": "Iteratively append the nearest feasible city that preserves feasibility.",
                "method": "deterministic distance-based selection with constraint filters; break ties by city index."
            },
            {
                "id": "local_improvement",
                "purpose": "Apply a simple, interpretable 2-opt-like local improvement to refine the tour without breaking constraints.",
                "method": "swap adjacent segments if improves cost and keeps feasibility."
            },
            {
                "id": "failure_replay_compression",
                "purpose": "Store compact, deterministic failure patterns to avoid known dead-ends on future runs.",
                "method": "maintain a small, fixed-size archive of constraint-violating prefixes; use to prune choices."
            }
        ],
        "constraints_handling": {
            "types": [
                "precedence",
                "capacity/resource",
                "forbidden_edges",
                "mandatory_cities",
                "visit_once"
            ],
            "representation": "per-city attribute flags and simple adjacency restrictions; no stochastic penalties.",
            "example": {
                "precedence": { "A": ["B", "C"] },
                "capacity": { "vehicle_capacity": 3, "city_loads": {"D": 1, "E": 2} },
                "forbidden_edges": [("X", "Y"), ("Y", "Z")],
                "mandatory_cities": ["S1", "S2"]
            }
        },
        "output_schema": {
            "tour": "list of city identifiers in visit order",
            "cost": "total distance or cost of the tour",
            "status": "feasible|infeasible|completed_with_constraints",
            "diagnostics": [
                "constraint_violations",
                "applied_tie_breakers",
                "compression_hits",
                "local_improvements_applied"
            ]
        },
        "determinism": {
            "seed_dependency": False,
            "randomized_components": False,
            "reproducibility_notes": "All decisions are deterministic: distances, indices, and constraint checks drive the flow; ties broken by city index."
        },
        "notes": [
            "This scaffold provides a structure to plug in real distance data and constraint definitions for a constrained TSP.",
            "Failure_replay_compression is intentionally lightweight to keep the design robust and interpretable."
        ]
    }
