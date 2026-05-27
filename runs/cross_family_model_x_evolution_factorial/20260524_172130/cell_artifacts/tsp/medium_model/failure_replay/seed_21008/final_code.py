def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold is designed for robustness and interpretability,
    # with a simple, replayable strategy suitable for held-out TSPLIB and synthetic transfers.
    # Keys:
    # - name: descriptor
    # - strategy: high-level approach
    # - components: modular steps with deterministic parameters
    # - constraints: problem constraints assumed
    # - features: features used by the heuristic
    # - parameters: fixed, non-leaky parameters for reproducibility
    # - evaluation: lightweight scoring placeholders
    return {
        "name": "deterministic_constrained_tsp_scaffold_v1",
        "strategy": "greedy-constrained-insertion with feasibility check and repair",
        "description": (
            "A simple, interpretable heuristic that builds a Hamiltonian cycle by iteratively "
            "inserting the next node in a position that minimally increases tour cost while "
            "satisfying degree and constraint feasibility. It uses deterministic tie-breaking "
            "and a repair step to enforce feasibility in case of violations."
        ),
        "constraints": {
            "max_degree_per_node": 2,  # TSP tour constraint
            "min_tour_ratio": 0.98,     # heuristic accepts near-complete tours
            "feasibility_checks": ["degree", "subtour_free", "constrained_nodes"],
            "deadlock_lock": True        # deterministic handling of equal-cost insert positions
        },
        "components": [
            {
                "name": "initial_seed",
                "description": "Start with a fixed small seed tour to guarantee determinism.",
                "params": {
                    "seed_nodes": [0, 1],  # deterministic starting edge if present
                    "shuffle": False
                }
            },
            {
                "name": "cost_function",
                "description": "Deterministic edge cost function based on provided distance matrix.",
                "params": {
                    "distance_matrix_access": "direct",
                    "tie_breaker": "index"  # break ties by node index
                }
            },
            {
                "name": "insertion_step",
                "description": "Insert the remaining nodes one by one in the position that yields minimal incremental cost.",
                "params": {
                    "feasibility": "check_all",
                    "tie_breaking": "lowest_increment_then_index",
                    "eligible_nodes_order": "ascending_by_index"  # deterministic
                }
            },
            {
                "name": "feasibility_repair",
                "description": "If a violation occurs (e.g., subtour, degree), perform a deterministic repair to restore a valid tour.",
                "params": {
                    "method": "subtour_merge_by_min_increment",
                    "max_iterations": 10
                }
            },
            {
                "name": "finalization",
                "description": "Close the tour if not already closed; ensure exact 2-regular tour.",
                "params": {
                    "close_tour_if_needed": True,
                    "verification": "complete_degree_two"
                }
            }
        ],
        "features": [
            "node_indices",
            "edge_costs",
            "cumulative_cost",
            "feasibility_flags",
            "subtour_detection"
        ],
        "parameters": {
            "distance_scaling": 1.0,
            "random_seed": 42,  # deterministic seed for any internal randomness (none used)
            "max_tour_length": None  # not used; tour length equals number of nodes
        },
        "evaluation": {
            "robustness_focus": [
                "held-out_TSP_libs",
                "synthetic_transfer_nodes",
                "mitigate_overfitting_to_training_instances"
            ],
            "metrics": [
                "tour_cost",
                "feasibility_rate",
                "subtour_count",
                "runtime_ms"
            ],
            "expected_behavior": "deterministic outputs for a given distance matrix"
        }
    }
