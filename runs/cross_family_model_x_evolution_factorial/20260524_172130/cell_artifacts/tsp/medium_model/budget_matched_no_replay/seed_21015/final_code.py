def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "description": "Deterministic constrained TSP heuristic scaffold with budget-matching and interpretable steps.",
        "version": "1.0",
        "budget_strategy": "budget_matched_no_replay",
        "assumptions": [
            "exact node coordinates or distance function are provided externally",
            "must respect a predefined budget of moves or total distance",
            "no replay memory, no failure memory, no compression",
            "no stochastic randomness; deterministic decisions based on input data"
        ],
        "constraint_handling": {
            "constraints": [
                "visit each node exactly once (standard TSP constraint)",
                "subset of nodes may be forbidden or prioritized by external budget",
                "budget is enforced as an upper bound on total distance or number of edges",
                "feasibility is checked after each extension"
            ],
            "priority": [
                "feasible solution if possible within budget",
                "if multiple feasible extensions exist, prefer smallest incremental distance",
                "prefer routes that enable future feasibility (lookahead up to a small fixed horizon)"
            ]
        },
        "heuristic_components": {
            "initialization": {
                "pivot_node": "first_node_in_input_order",
                "unvisited": "ordered_list_of_all_nodes_except_pivot",
                "current_node": "pivot_node",
                "accumulated_cost": 0,
                "path": ["pivot_node"]
            },
            "extension_rule": [
                "select next_node from unvisited with minimal incremental_distance_to_current_node",
                "tie-break by second_minimal_incremental_distance",
                "if all options would exceed budget, terminate with current path if feasible",
                "if no feasible extension exists and budget allows, attempt to backtrack minimally within one step (but no replay memory is used; backtracking is purely local and deterministic)"
            ],
            "budget_management": {
                "budget_type": "global",
                "budget_value": "provided per-instance via external interface",
                "update": "accumulated_cost += distance(current_node, next_node)",
                "feasibility_check": "accumulated_cost + lower_bound_to_complete_path <= budget_value",
                "lower_bound_to_complete_path": "estimate as sum of 2 * (minimum spanning tree heuristic) or zero if not computable in this scaffold"
            },
            "termination": {
                "complete_visit": "when all nodes visited",
                "budget_exceeded": "if no feasible extension and cannot complete path within budget, terminate with best-so-far feasible path",
                "finalization": "return to_start_node if required by constraints and budget"
            }
        },
        "scalability_and_interpretability": {
            "data_structures": {
                "path": "list of node identifiers in visitation order",
                "unvisited": "set or list supporting deterministic iteration",
                "costs": "dictionary or function calls to compute distances deterministically",
                "limits": "no heavy precomputation; distance lookups are assumed to be provided by external distance function"
            },
            "interpretability_features": [
                "explicit path sequence",
                "explicit cost at each step",
                "explicit budget remaining",
                "rationale comments in code paths for deterministic choices"
            ]
        },
        "compatibility": {
            "input_interface": {
                "nodes": "ordered collection of node IDs or coordinates; distance function to be provided externally",
                "budget": "numeric upper bound on total tour length or number of edges",
                "distance_fn": "external callable: distance_fn(a, b) -> float (not serialized here; assumed available at runtime)"
            },
            "output_interface": {
                "path": "list of node IDs in visit order",
                "total_cost": "float total distance of returned path",
                "feasible": "bool indicating whether path respects budget and constraints"
            }
        }
    }
