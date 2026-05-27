def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (single-shot)
    # The dictionary encodes a simple, interpretable heuristic framework
    # with predefined components suitable for TSPLIB-like and synthetic tests.

    scaffold = {
        "name": "constrained_tsp_single_shot_heuristic",
        "version": 1,
        "description": "Deterministic, interpretable single-shot heuristic scaffold for constrained TSP.",
        "assumptions": {
            "nodes": "list or array of node identifiers with (optional) coordinates",
            "edges": "optional precomputed distances; if absent, Euclidean-like distances are assumed via coordinates",
            "constraints": [
                "max_route_distance",  # total allowed distance or budget
                "time_window"          # optional per-node time windows
            ],
            "start_node": "optional fixed start node",
            "end_node": "optional fixed end node",
        },
        "data_representation": {
            "nodes": "list of node dicts: {id, x, y, demand (optional), time_window (optional)}",
            "distances": "function or matrix accessor; if absent, compute on the fly from coordinates",
        },
        "scoring_function": {
            "objective": "minimize total_distance_within_constraints",
            "penalties": {
                "violation": "large_penalty for constraint violations",
                "early_stopping": "moderate_penalty if current partial path cannot satisfy remaining constraints"
            },
            "priority": ["feasibility", "shortest_path"],
        },
        "heuristic_strategy": {
            "type": "greedy_with_feasibility_filter",
            "steps": [
                "start from start_node if provided; otherwise pick smallest id",
                "maintain visited set and current_path",
                "at each step, evaluate candidate_next among unvisited nodes that satisfy immediate constraints (e.g., time window, remaining distance budget)",
                "choose candidate with best metric: (distance_to_candidate + penalty_if_constraint_violation) and prioritize feasibility",
                "terminate when all required nodes visited or no feasible extension remains"
            ],
            "distance_metric": "euclidean_like or given distance matrix; deterministic",
            "feasibility_rules": [
                "would not violate total budget if added",
                "time_window constraints if provided",
            ],
        },
        "robustness_features": {
            "held_out_performance": {
                "evaluation_sets": [
                    "standard TSPLIB constrained instances",
                    "synthetic_transfer_instances with varied densities and constraints"
                ],
                "measurement": [
                    "feasibility_rate",
                    "average_completion_distance",
                    "worst_case_distance",
                ],
            },
            "transfer_splits": {
                "train": "none in single_shot; scaffold is fixed",
                "validate": "deterministic test sets embedded in evaluation outside scaffold"
            }
        },
        "output_representation": {
            "path": "list of node ids in visiting order",
            "metrics": {
                "total_distance": "computed distance along path",
                "feasible": "boolean indicating all constraints satisfied",
                "visited_count": "number of nodes visited",
            }
        },
        "constraints": {
            "determinism": True,
            "no_external_io": True,
            "no randomness": True
        }
        ,
        "notes": "This scaffold is intended to be extended by an actual implementation in a separate module. It provides a deterministic blueprint with interpretable greedy-feasibility logic suitable for constrained TSP benchmarks."
    }

    return scaffold
