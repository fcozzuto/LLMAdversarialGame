def build_heuristic():
    """
    Deterministic heuristic scaffold for a constrained TSP heuristic
    using a budget_matched_no_replay approach with candidate 1.
    Returns a dictionary describing the heuristic configuration and constraints.
    """
    heuristic = {
        # Core strategy identifiers
        "strategy": "budget_matched_no_replay",
        "version": 1,
        "name": "Candidate1_constrained_TSP_heuristic",
        
        # Problem framing
        "problem": {
            "type": "constrained_tsp",
            "constraints": {
                "mandatory_nodes": [],
                "forbidden_edges": [],
                "time_window": None,
                "capacity": None
            },
            "instances": {
                "tsplib": ["A", "B", "C", "D"]  # deterministic placeholder identifiers
            }
        },
        
        # Heuristic components
        "components": {
            "initial_solution": {
                "method": "nearest_neighbor_with_constraints",
                "parameters": {
                    "start_node": 0,
                    "allow_revisit": False,
                    "random_seed": 42  # deterministic seed
                }
            },
            "local_search": {
                "method": "2_opt_with_constraint_checks",
                "parameters": {
                    "iterations": 100,
                    "verify_feasibility": True,
                    "acceptance_criterion": "improvement_only",
                    "random_seed": 42
                }
            },
            "insertion_mutation": {
                "method": "segment_insertion",
                "parameters": {
                    "max_segment_length": 3,
                    "time_budget_fraction": 0.25
                }
            },
            "repair": {
                "method": "constraint_compliance",
                "parameters": {
                    "repair_strategy": "minimal_changes",
                    "monitor_metrics": ["feasibility", "constraint_violations"]
                }
            }
        },
        
        # Budgeting and selection
        "budget": {
            "total_steps": 500,
            "step_allocation": {
                "initial_solution": 150,
                "local_search": 250,
                "mutation": 50,
                "repair": 50
            },
            "adaptive_budget": False,
            "time_limit_seconds": 60
        },
        
        # Transfer and robustness considerations
        "robustness": {
            "held_out_tsplib_focus": True,
            "synthetic_transfer": {
                "generate_from_training": False,
                "seed": 42,
                "scaling": {
                    "node_count_range": [20, 60],
                    "density": "moderate"
                }
            },
            "interpretability": True,
            "logging": {
                "level": "INFO",
                "record_metrics": ["feasibility", "objective_value", "runtime"]
            }
        },
        
        # Outputs and reproducibility
        "outputs": {
            "solution_representation": "sequence_of_nodes",
            "objective": "tour_cost",
            "feasibility_report": True
        }
    }
    return heuristic
