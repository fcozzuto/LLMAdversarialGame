def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a simple, interpretable plan.
    # This scaffold is a single-shot heuristic and does not rely on imports or external data.
    scaffold = {
        "name": "single_shot_constrained_tsp",
        "version": "1.0",
        "description": "Deterministic single-shot heuristic for constrained TSP with interpretability.",
        "technique": "single_shot",
        "assumptions": {
            "distance_metric": "euclidean",
            "triangle_inequality": True,
            "city_positions": "provided_at_runtime",
            "constraints": {
                "limits": "hard_constraints_only",
                "types": ["capacity", "time_window"],  # examples; enforceable in runtime
                "verification": "feasible_solution_required"
            }
        },
        "procedure": [
            {
                "step": 1,
                "action": "initialize",
                "details": "Start with a smallest feasible path from a designated depot (node 0)."
            },
            {
                "step": 2,
                "action": "construct_candidates",
                "details": "For each step, generate candidate next-city by sorted nearest-neighbor order with a deterministic tie-break (city index)."
            },
            {
                "step": 3,
                "action": "build_path",
                "details": "Iteratively append the nearest feasible city that does not violate hard constraints. If none fit, stop and backtrack minimally to maintain feasibility."
            },
            {
                "step": 4,
                "action": "feasibility_check",
                "details": "After path completion, verify all constraints are satisfied (capacity, time windows). If violated, apply deterministic repair by local swap within a small window to restore feasibility."
            },
            {
                "step": 5,
                "action": "termination",
                "details": "Return the constructed tour if feasible; otherwise return a best-effort feasible sub-tour with a note."
            }
        ],
        "data_structures": {
            "tour": "list of vertex indices in visitation order",
            "visited": "set for O(1) membership checks",
            "cost": "accumulated tour length",
            "constraints_state": "structure capturing remaining capacity and time windows"
        },
        "outputs": {
            "tour": "list of integers representing the order of visits starting from depot",
            "total_cost": "float",
            "feasible": "bool",
            "diagnostics": {
                "steps_taken": "integer",
                "backtracks": "integer",
                "constraint_violations_resolved": "integer"
            }
        },
        "robustness_considerations": [
            "deterministic tie-breaking by city index",
            "explicit feasibility verification and deterministic repair path",
            "works with standard TSPLIB-like inputs and synthetic extensions",
            "no stochastic components or randomness"
        ],
        "example_protocol": {
            "input_signature": {
                "cities": "list of (x, y) pairs, index 0 as depot",
                "demands": "list of non-negative numbers aligned with cities (0 for depot)",
                "capacities": "single scalar capacity for the vehicle",
                "time_windows": "list of (start, end) pairs per city or None"
            },
            "expected_output": {
                "tour": "sequence of city indices",
                "total_cost": "float",
                "feasible": "bool"
            }
        }
    }
    return scaffold
