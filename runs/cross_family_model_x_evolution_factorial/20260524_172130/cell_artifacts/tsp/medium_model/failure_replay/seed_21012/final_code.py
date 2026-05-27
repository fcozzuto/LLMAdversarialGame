def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with deterministic transfers and held-out evaluation emphasis.",
        "assumptions": [
            "Graph is complete with non-negative edge costs.",
            "Constraints are represented as a set of forbidden edges and/or mandatory visit orders.",
            "Heuristic is interpretable and not overly complex.",
            "Deterministic behavior: no randomness; identical inputs yield identical outputs."
        ],
        "representation": {
            "nodes": "List of node identifiers (integers or strings).",
            "edges": "Implicit complete graph inferred from node list and distance function; explicit forbidden or required edges may be provided.",
            "constraints": {
                "forbidden_edges": "Set of edge tuples (i, j) that must not be used.",
                "required_order": "List of node pairs (a, b) indicating a must precede b.",
                "mandatory_nodes": "Subset of nodes that must be included in the tour if relevant."
            }
        },
        "core_components": {
            "preprocessing": [
                "Validate node list and constraint consistency.",
                "Build adjacency-like distance matrix on demand using a provided distance function contract.",
                "Detect trivially infeasible constraint sets (e.g., conflicting required orders)."
            ],
            "construction_strategy": [
                "Greedy-feasible extension with constraint checks.",
                "Maintain a current path; at each step, select the feasible next node that minimally increases path cost and respects constraints.",
                "If no feasible next node exists, trigger a controlled backtrack limited to a small depth to recover a valid prefix."
            ],
            "constrained_checks": [
                "Edge not in forbidden_edges must be avoided.",
                "Adding a candidate edge must not violate immediate feasibility with respect to required_order and future reachability assumptions.",
                "When required_order is present, ensure all prerequisites are scheduled before successors when exploring candidates."
            ],
            "termination": [
                "Tour includes all nodes exactly once if mandatory_nodes and constraints allow a Hamiltonian path",
                "If a full Hamiltonian tour is not feasible under constraints, return best-feasible partial tour with an explicit feasibility flag."
            ]
        },
        "heuristic_outputs": {
            "tour": "List of node identifiers in visitation order.",
            "cost": "Total cost of the produced tour; high-cost value indicates infeasibility.",
            "feasible": "Boolean flag indicating whether the produced tour satisfies all constraints.",
            "diagnostics": {
                "constraint_violations": "Count or list of violations observed (if any).",
                "backtracks_used": "Integer count of backtracking steps performed.",
                "notes": "Optional explanatory notes for interpretability."
            },
            "runtime_characteristics": {
                "determinism": True,
                "scalability_hint": "O(n^2) in the worst-case for naive greedy with small backtracking depth."
            }
        },
        "example_interface_contract": {
            "input": {
                "nodes": ["A","B","C","D"],
                "forbidden_edges": [("A","D")],
                "required_order": [("B","C")],
                "mandatory_nodes": ["A","B","C","D"]
            },
            "output": {
                "tour": ["A","B","C","D"],
                "cost": None,
                "feasible": True,
                "diagnostics": {
                    "constraint_violations": [],
                    "backtracks_used": 0,
                    "notes": "Deterministic greedy with one-step feasibility checks."
                }
            }
        }
    }
