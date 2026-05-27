def build_heuristic():
    # Deterministic TSP heuristic scaffold using a simple, interpretable approach.
    # This scaffold emphasizes robustness across held-out TSPLIB-like instances and
    # synthetic transfers without relying on random imports or external data.
    scaffold = {
        "name": "deterministic_robust_tsp_heuristic",
        "description": "A simple, interpretable held-out-friendly heuristic scaffold for constrained TSP.",
        "technique": "random_replay",
        "notes": "Candidate 1. No replay archive entries available. Deterministic construction.",
        "parameters": {
            "seed": 42,
            "initial_solution": "nearest_neighbor_with_tiebreak",
            "neighborhood_search": "2-opt",
            "constrained_handling": {
                "constraints": ["need_to_visit_all_matches", "time_budget"],
                "strategy": "feasible_inference_only"
            },
            "termination": {
                "max_iterations": 100,
                "improvement_threshold": 1e-6
            },
            "robustness_promises": [
                "prefers solutions that generalize to TSPLIB-like instances",
                "balances exploration with deterministic refinement",
                "avoid overfitting to synthetic training-only patterns"
            ]
        },
        "structure": {
            "overview": "A two-stage deterministic scaffold: (1) construct a deterministic initial tour; (2) apply a fixed, interpretable local search to improve feasibility and cost within constrained rules.",
            "initial_solution_method": {
                "name": "nearest_neighbor_with_tiebreak",
                "details": "At each step, choose the closest unvisited city; if ties, break by smallest index (deterministic)."
            },
            "local_search_method": {
                "name": "2-opt_fixed",
                "details": "Apply 2-opt moves in a fixed, deterministic order over edges to improve cost while preserving feasibility.",
                "order": "increasing edge_index order",
                "feasibility_check": "all_constraints_satisfied_after_move"
            },
            "constraint_handling": {
                "approach": "hard-feasibility-first",
                "fallback": "if infeasible, revert move and continue",
                "budget_respect": "ensure total_distance within conservative bound for on-time solutions"
            }
        },
        "evaluation": {
            "held_out_focus": [
                "TSPLIB-like instances",
                "synthetic_transfer-like graphs with varied density",
                "avoid overfitting to training distribution"
            ],
            "metrics": {
                "tour_length": "final_path_cost",
                "feasibility": "constraint_satisfaction_flag",
                "computational_efficiency": "runtime_units"
            }
        }
    }
    return scaffold
