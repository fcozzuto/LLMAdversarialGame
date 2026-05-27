def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using budget_matched_no_replay idea.
    # This scaffold emphasizes robustness across TSPLIB-like and synthetic instances,
    # while keeping interpretation simple and avoiding replay/failure memory.

    heuristic = {
        "name": "budget_matched_no_replay_scaffold",
        "version": 1.0,
        "description": (
            "Deterministic constrained TSP heuristic scaffold using a budget-matched "
            "greedy construction with simple feasibility checks and local improvement."
        ),
        # Problem definition
        "problem": {
            "type": "constrained_tsp",
            "constraints": {
                "max_subtour_length": None,       # optional constraint (can be set by user)
                "mandatory_edges": [],            # list of (u, v) tuples that must be included
                "forbidden_edges": [],            # list of (u, v) tuples that must be avoided
                "must_visit": [],                   # subset of nodes that must be included (in practice all nodes)
            },
            "budget": {
                "budget_type": "distance",
                "allow_revisit": False,
                "max_total_distance": None,         # if set, the tour must not exceed this value
            },
        },
        # Heuristic strategy (deterministic, no randomness, no replay)
        "strategy": {
            "initialization": {
                "start_node": 0,                    # deterministic starting node
                "visited_order": [],                 # to be populated by construction
                "unvisited_set": "dynamic",          # internal representation
            },
            "construction": {
                "method": "greedy_budget_match",
                "budget_propagation": True,
                "edge_selection": {
                    "criterion": "min_incremental_cost",
                    "tie_breaker": "lowest_current_degree",
                    "consider_constraints": True,
                },
                "feasibility_checks": [
                    "no_subtour_until_complete",
                    "respect_must_visit",
                    "respect_forbidden_edges",
                    "budget_remaining_sufficient_for_closure",
                ],
            },
            "refinement": {
                "local_search": {
                    "enabled": True,
                    "moves": ["2opt", "swap", "reverse_segment"],
                    "budget_constrained": True,
                    "iterations": 0,  # 0 indicates scaffolding; implementers can enable later
                }
            },
        },
        # Robustness considerations
        "robustness": {
            "transfer_horizon": {
                "tsplib_and_synthetic": True,
                "sequence": ["short", "medium", "long"],
            },
            "fallbacks": {
                "on_infeasibility": [
                    "return_partial_path_with_subtour_removal",
                    "flag_infeasible_and_continue",
                ],
                "budget_violation": ["trim_at_budget", "report_excess"],
            },
        },
        # Outputs and diagnostics
        "outputs": {
            "tour": [],
            "distance": None,
            "feasibility": False,
            "logs": [],
        },
        # Determinism and configuration exposure
        "determinism": {
            "seed": 0,                  # not used for randomness; fixed for determinism
            "reproducible": True,
            "ordering": "node_id_increasing",
        },
        # Example placeholder for compatibility with interfaces
        "interface": {
            "input_schema": {
                "nodes": "list[int]",
                "edges": "list[(int,int,float)]",
                "constraints": "dict",
            },
            "output_schema": {
                "tour": "list[int]",
                "distance": "float",
                "feasible": "bool",
            },
        },
        # Note: This scaffold is intentionally simple and interpretable.
        "scaffold_type": "budget_matched_no_replay",
        "notes": "Deterministic, no replay memory, no failure memory, no compression."
    }

    return heuristic
