def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic (single_shot: Candidate 1)
    # This dictionary encodes a compact, interpretable heuristic configuration
    # without external imports or training data dependencies.

    heuristic = {
        # Core strategy: construct a tour by a deterministic nearest-allowed-neighbor policy
        # with simple feasibility checks against a small set of constraints.
        "strategy": {
            "name": "deterministic_nearest_allowed_neighbor",
            "description": (
                "Builds a tour by always connecting to the nearest unvisited node that satisfies "
                "all problem-specific constraints (e.g., capacity, precedence, or domain bounds)."
            ),
            "parameters": {
                "distance_metric": "euclidean",  # assumes node positions are provided as (x, y)
                "tie_breaker": "node_id",        # deterministic tie-break by node id
                "constraint_check": True
            }
        },
        # Constraint handling
        "constraints": {
            # Example constraint keys; actual feasibility functions are expected to be provided
            # by the consumer of this scaffold. Values here indicate presence and simple rules.
            "types": ["capacity", "precedence", "time_window"],
            "capacity": {
                "max_load_per_route": 100  # arbitrary deterministic bound
            },
            "precedence": {
                "enabled": True
            },
            "time_window": {
                "enabled": False  # off by default for robustness; can be enabled in extended use
            }
        },
        # Initialization and termination
        "initialization": {
            "start_node_rule": "lowest_id",
            "seed": 1  # deterministic seed for any internal randomness (if any)
        },
        "termination": {
            "route_completion": "when_all_nodes_visited_or_no_feasible_extension",
            "max_steps": 1000
        },
        # Node/instance representation
        "domain": {
            "nodes": {
                "description": "Each node must be provided by the instance: id, x, y, demand, capacity",
                "required_fields": ["id", "x", "y", "demand"]
            },
            "edges": {
                "description": "Implicit complete graph; distances computed as Euclidean between node coordinates",
                "distance_function": "euclidean"
            }
        },
        # Performance and robustness signals (held-out evaluation targets)
        "performance": {
            "held_out_evaluation": {
                "tsplib_robustness": True,
                "synthetic_transfer": True,
                "metric": "tour_cost_per_node",
                "aggregation": "median_over_runs",  # deterministic runs ensure low variance
                "risk_flags": ["avoid_overfitting_to_training_instances"]
            }
            ,
            "scalability": {
                "intent": "linear_or_sublinear_with_nodes",
                "max_nodes_considered": 500
            }
        },
        # Interpretability and simplicity
        "interpretability": {
            "notes": [
                "One-pass constructive heuristic with deterministic decisions.",
                "No learned parameters; all rules derive from explicit policy.",
                "Easily inspectable: chosen next node, feasibility check outcome, and remaining demand."
            ],
            "logging": {
                "enabled": True,
                "level": "INFO"
            }
        },
        # Optional extensibility hooks (placeholders)
        "extensions": {
            "feasibility_checker": "provided_by_user",
            "distance_cache": "not_required_by_default"
        },
        # Return type hint surrogate
        "__return_type__": "dict"
    }

    return heuristic
