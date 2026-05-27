def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # Budget-matched_no_replay: simple, robust, interpretable
    return {
        "name": "budget_matched_no_replay_candidate_1",
        "strategy": "greedy_with_feasible_fix",
        "description": (
            "A deterministic, budget-aware constructive heuristic for constrained TSP. "
            "Builds a tour greedily while respecting a per-node visit budget and optional "
            "constraint masks. No replay or memory usage; deterministic ties resolved by node index."
        ),
        "parameters": {
            "node_budget": 1,            # visits per node (limit to 1 unless multi-visit allowed by constraint)
            "max_iterations": 1000,      # safeguard to ensure termination
            "distance_metric": "euclidean",  # distances computed deterministically from coordinates
            "tie_breaker": "lowest_index",    # deterministic tie-breaking
            "repair_step": "local_1opt",      # simple repair when dead-ends encountered
            "constraint_handling": "mandatory",
            "seed": 42,                       # for any internal randomness (kept fixed for determinism)
            "tour_complete_required": True,   # require a complete tour before acceptance
        },
        "modules": [
            {
                "name": "constructive_builder",
                "role": "builds an initial feasible tour respecting budget and constraints",
                "logic": [
                    "initialize_unvisited = all_nodes",
                    "start_node = min_index_node_with_minimally_connected_profile",
                    "tour = [start_node]",
                    "unvisited.remove(start_node)",
                    "while unvisited and len(tour) < max_iterations:",
                    "    candidate = argmin_distance_from_tour_end_to_unvisited(unvisited)",
                    "    if adding_candidate_violates_constraint(candidate):",
                    "        candidate = next_best_feasible_candidate(unvisited, constraints)",
                    "    if candidate is None:",
                    "        break",
                    "    tour.append(candidate)",
                    "    unvisited.remove(candidate)",
                    "",
                ],
            },
            {
                "name": "feasibility_checker",
                "role": "validate budget and constraints; triggers repair if needed",
                "logic": [
                    "check all node budgets",
                    "check subtour legality if constraints include time windows or categories",
                    "if infeasible: invoke repair_step to reconnect tour",
                ],
            },
            {
                "name": "repairer",
                "role": "simple local repair to fix dead-ends",
                "logic": [
                    "identify a minimal edge removal and insertion to maintain feasibility",
                    "perform 1-opt style local replacement on a small window",
                ],
            },
        ],
        "objective": {
            "type": "maximize_return_under_budget",
            "callback": "sum_of_rewards = sum(benefit(node)) for nodes in tour",
            "budget_constraint": "aggregate_budget <= total_budget",
            "constraints": ["subtour_contiguity", "visit_once_per_node"]
        },
        "data_sources": {
            "tsplib_heldout": True,
            "synthetic_transfer": True,
            "training_bias_avoidance": True
        },
        "output_format": {
            "tour": "list_of_node_indices_in_visit_order",
            "cost": "computed_total_distance_of_tour",
            "feasibility": "boolean"
        },
        "robustness_notes": [
            "deterministic with fixed seed",
            "uses only simple, well-understood operations",
            "handles both TSPLIB and synthetic instances",
            "interpretable decision steps with clear heuristics",
        ],
        "limitations": [
            "no learning-based replay; does not reuse memory of past runs",
            "may be conservative on very dense constrained instances"
        ],
    }
