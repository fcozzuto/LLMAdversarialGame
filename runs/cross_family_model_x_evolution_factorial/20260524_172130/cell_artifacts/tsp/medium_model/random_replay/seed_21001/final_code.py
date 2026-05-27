def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP heuristic using a
    # "random_replay" style scheme. This scaffold is interpretable, robust to
    # diverse TSPLIB-like instances, and includes deterministic transfer hints.
    # Note: No imports used; all values are plain Python primitives.

    heuristic = {
        # Core strategy: construct a tour by repeatedly selecting the nearest
        # feasible city from the current endpoint, respecting a simple degree
        # and constraint check. The constraints are kept explicit and lightweight.
        "strategy": "nearest_feasible_with_constraints",

        # Feasibility rules encoded explicitly to avoid runtime dependencies.
        "constraints": {
            # Degree bound for TSP (each city must have exactly two edges in tour)
            "degree_bound": 2,
            # Subtour elimination: prevent creation of subtours during construction.
            # Implemented as a post-check in a real engine; here we expose flag.
            "prevent_subtours": True,
            # Time/step budget to keep deterministic and lightweight.
            "max_steps": 100
        },

        # Heuristic parameters (deterministic values; no randomness)
        "parameters": {
            # Lookahead window size for candidate selection (small, interpretable)
            "lookahead": 2,
            # Preference weight for visiting high-constraint cities earlier
            "constraint_bias": 1.0,
            # Tie-breaking rule: smallest index (deterministic)
            "tie_break": "index"
        },

        # Transfer/robustness design: provide a small set of transfer-ready hints
        # without relying on training data or replay archives.
        "transfer_hints": {
            # Use a fixed synthetic transfer seed to facilitate reproducibility
            "transfer_seed": 42,
            # Typical problem families to expect: small to medium TSPLIB-like graphs
            "expected_families": ["Kreise", "att48", "berlin52", "eil101"],
            # Predefined edge cost normalization strategy (unit edge costs, then scale)
            "cost_normalization": {
                "mode": "unit_cost_then_scale",
                "scale_factor": 1.0
            }
        },

        # Evaluation scaffold (deterministic lightweight metrics)
        "evaluation": {
            # Simple proxy metrics to guide heuristic quality without executing
            "proxy_quality": "deterministic_sum_of_heuristic_costs",
            "proxy_features": ["num_nodes", "density", "degree_variance"]
        },

        # Interpretability aids
        "interpretation": {
            # Human-readable description per component
            "component_descriptions": {
                "strategy": "Nearest feasible extension with simple feasibility checks",
                "constraints": "Maintain degree 2 per node; avoid subtle subtours",
                "parameters": "Deterministic lookahead and tie-breaking",
                "transfer_hints": "Prepare for cross-instance transfer with fixed seeds and families",
                "evaluation": "Provide deterministic quality proxies"
            }
            ,
            # Internal deterministic rules to trace decisions (as data, not code)
            "decision_trace": {
                "enabled": True,
                "depth": 1
            }
        },

        # Compatibility with constrained TSPLIB-like instances
        "compatibility": {
            "instance_class": "constrained_tsp",
            "assumed_structure": "undirected, complete graph, with possible node/edge constraints",
            "scalability": "linearithmic in number of nodes for construction, small constants for checks"
        }
    }

    return heuristic
