def build_heuristic():
    # Deterministic, interpretable constrained TSP heuristic scaffold
    # Single-shot candidate: robust, with held-out TSPLIB and synthetic transfer considerations.
    scaffold = {
        # Basic problem metadata (assumed known by consumer)
        "problem_type": "constrained_tsp",
        "version": 1,
        "description": "Deterministic, interpretable scaffold for constrained TSP heuristic",
        
        # Heuristic strategy components
        "strategy": {
            # 1. Seed route construction: greedy with feasibility checks
            "seed_construction": {
                "method": "greedy_feasible",
                "feasibility_checks": [
                    "capacity_limits",
                    "precedence_constraints",
                    "exclusive_visited_regions",
                ],
                "tie_breaker": "lowest_cost_increment",
                "random_seed": 0  # deterministic
            },
            # 2. Local improvement: 2-opt-like refinement with constraint preservation
            "local_improvement": {
                "method": "feasible_two_opt",
                "max_iterations": 100,
                "convergence_criterion": "no_improvement_within_batch",
                "allow_swaps": [
                    "edge_replacement",
                    "swap_2opt",
                ],
                "constraint_handling": "post_check_and_repair",
            },
            # 3. Repair and feasibility enforcement
            "repair_mechanism": {
                "enabled": True,
                "approach": "constraint_propagation",
                "fallback": "partial_rebuild",
            },
            # 4. Handling of fixed/mandatory nodes and regions
            "mandatory_nodes": {
                "spec": "explicit_list",
                "source": "instance_metadata",
                "handling": "must_visit",
            },
            "forbidden_edges": {
                "spec": "explicit_list",
                "source": "instance_metadata",
                "handling": "cannot_use",
            }
        },
        
        # Performance and robustness considerations
        "evaluation_criteria": {
            "quality": "feasible_route_cost",
            "robustness": "stable_across_held_out_tsplib",
            "transfer_focus": "synthetic_and_tsplib",
            "computation_budget": {
                "time_ms": 2000,
                "solution_steps": 5000
            }
        },
        
        # Data representation
        "data_schema": {
            "cities": "list_of_city_objects",
            "edges": "optional_adjacency_or_cost_matrix",
            "constraints": {
                "capacity": "max_tour_cost_or_resource",
                "precedence": "order_constraints",
                "region_visits": "disjoint_or_fixed_limits"
            }
        },
        
        # Interpretability aids
        "interpretability": {
            "logics": [
                "seed_cost_increase_analysis",
                "improvement_delta_tracking",
                "feasibility_violation_report"
            ],
            "debug_flags": {
                "verbose": False,
                "checkpoints": [10, 50, 100]
            }
        },
        
        # Deterministic defaults
        "random_seed": 0,
        "reproducibility": {
            "enable": True,
            "seed_source": "constant"
        }
        
        # End of scaffold
    }
    return scaffold
