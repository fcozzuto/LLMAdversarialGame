def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic
    # This structure is interpretable and avoids external imports.
    # It emphasizes robust held-out TSPLIB and synthetic transfer considerations.
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": (
            "A lightweight, interpretable heuristic scaffold for constrained TSP. "
            "Prioritizes deterministic behavior, robustness to held-out TSPLIB-like "
            "instances, and straightforward transfer to synthetic test cases."
        ),
        "assumptions": {
            "distance_metric": "euclidean",
            "triangle_inequality": True,
            "node_visibility": "all",
            "demands_present": True,
            "capacities_present": True,
            "time_window_constraints": False,
        },
        "parameters": {
            "initial_solution_strategy": "greedy_nearest_neighbor_with_constraints",
            "local_search": "2-opt",
            "repair_method": "simple_insertion_with_constraints",
            "rotation_cutoff": 0.05,  # fraction of nodes allowed to be reassigned during repair
            "penalties": {
                "violation_penalty": 1000.0,  # high to discourage violations
                "capacity_penalty": 500.0,
            },
            "stopping_criteria": {
                "time_limit_seconds": 60.0,
                "iterations": 200,
                "improvement_cutoff": 1e-4,
            },
        },
        "pipeline": [
            {
                "stage": "initialization",
                "description": (
                    "Create an initial feasible tour using a greedy nearest-neighbor path "
                    "that respects node demands and vehicle capacities heuristically."
                ),
                "operations": [
                    "select_start_node deterministically (e.g., smallest index)",
                    "build_ordered_list by repeatedly choosing nearest feasible next node",
                    "ensure capacity constraints are not violated by current partial tour"
                ],
                "outputs": ["partial_tour", "unvisited_nodes"]
            },
            {
                "stage": "repair_and_improve",
                "description": (
                    "Repair infeasibilities and apply a constrained 2-opt local search "
                    "on the feasible portion of the tour."
                ),
                "operations": [
                    "detect_capacity_violations",
                    "insert_feasible_nodes from unvisited set where possible",
                    "perform_constrained_2opt(): swap edges only if constraints remain feasible"
                ],
                "outputs": ["feasible_tour"]
            },
            {
                "stage": "finalization",
                "description": (
                    "Finalize tour by closing the loop and performing a final feasibility check."
                ),
                "operations": [
                    "close_tour_to_start",
                    "validate_all_constraints",
                    "compute_cost"
                ],
                "outputs": ["final_tour", "final_cost"]
            }
        ],
        "data_handling": {
            "held_out_testing": {
                "tsplib_like": True,
                "synthetic_transfer": True,
                "random_seed_reproducible": True,
            },
            "normalization": {
                "scale_demand": False,
                "normalize_distance": False
            }
        },
        "metrics": {
            "cost": "total_distance",
            "feasibility": "all_constraints_satisfied",
            "robustness": "performance_on_held_out",
            "transfer_potential": "synthetic_vs_tsplib_performance_diff"
        },
        "notes": [
            "Deterministic seed-based operations; no randomness in this scaffold.",
            "Intended as a readable starting point for implementing a constrained TSP heuristic.",
            "Can be extended with actual distance computations and constraint checks in a follow-up."
        ]
    }
