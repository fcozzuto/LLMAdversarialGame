def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold is interpretable and balances robustness across TSPLIB-like
    # and synthetic transfer scenarios without relying on external imports.
    return {
        "name": "deterministic_constrained_tsp_scaffold",
        "version": "1.0",
        "description": (
            "A simple, interpretable heuristic scaffold for constrained TSP. "
            "Uses a deterministic greedy construction with configurable priorities "
            "to ensure robust performance on held-out TSPLIB-like instances and "
            "synthetic transfers. No randomness or external imports."
        ),
        "parameters": {
            "seed": 0,  # kept for compatibility; deterministic by design
            "use_distance_to_constraints": True,
            "prefer_nearby_unvisited": True,
            "constraint_penalty": 1.0,
            "max_route_length_ratio": 1.25,  # allow slight overflow beyond nominal length
            "priority_weights": {
                "distance": 1.0,
                "constraint_satisfaction": 1.0,
                "unvisited_balance": 0.5
            }
        },
        "algorithm": {
            "type": "greedy_constrained_construction",
            "description": (
                "Begin at an arbitrary fixed start node. Iteratively append the nearest "
                "unvisited node that does not violate the cumulative route length budget "
                "or major constraint violations. If no compliant neighbor exists, "
                "choose the next best feasible candidate that minimally breaches a constraint."
            ),
            "steps": [
                "Set current_node to starting_node (node with index 0).",
                "Maintain visited set and route list.",
                "While unvisited nodes remain:",
                "    Build candidate list: unvisited nodes sorted by a composite score.",
                "    Composite score combines distance, constraint_violation, and balance.",
                "    Select the first candidate that keeps route feasible under max length.",
                "    If none feasible, select the closest feasible node under relaxed constraint.",
                "    Append selected node to route, mark visited, update current_node.",
                "Return the ordered route as the solution sequence.",
            ],
            "computation": "deterministic evaluation of scores without randomness.",
        },
        "risk_management": {
            "fallback_behaviors": [
                "If route cannot be completed within max_route_length_ratio, terminate with current route.",
                "If start node chosen leads to poor coverage, still produce deterministic route for reproducibility.",
            ],
            "plausible_limitations": [
                "Greedy approach may not guarantee optimal constrained tour.",
                "Performance sensitive to starting_node choice; fixed to node 0 for determinism."
            ]
        },
        "robustness_focus": {
            "held_out_tsplib": {
                "intent": "perform consistent heuristic on standard benchmark-like graphs.",
                "strategy": "avoid reliance on instance-specific heuristics; use distance-based scoring."
            },
            "synthetic_transfer": {
                "intent": "stable transfer across synthetic variations; penalize constraint violations consistently.",
                "strategy": "constant weights and budgets across transfers, no stochastic variation."
            }
        },
        "interfaces": {
            "input": {
                "nodes": "list of node coordinates or abstract positions. Each node must be indexable by integer.",
                "dimensions": "int indicating coordinate dimensionality (2 or higher).",
                "distance_fn": "optional; if not provided, Euclidean distance is assumed (deterministic).",
                "constraints": "optional constraints dict, e.g., required nodes, time windows (simplified)."
            },
            "output": {
                "route": "list of node indices in visitation order",
                "cost": "float representing total tour length (with possible termination early).",
                "feasible": "bool indicating whether route respects major constraints."
            }
        }
    }
