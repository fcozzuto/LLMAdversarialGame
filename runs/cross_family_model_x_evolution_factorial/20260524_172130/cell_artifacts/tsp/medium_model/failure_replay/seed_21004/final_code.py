def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSPLIB-style TSP heuristic with robust planning for held-out TSPLIB and synthetic transfer performance.",
        "assumptions": [
            "Problem is a symmetric or asymmetric TSP with optional constraints (e.g., forbidden edges, mandatory visits, capacity-like constraints).",
            "Inputs include a distance matrix or coordinates, a set of constraints, and optional site/edge penalties.",
            "Deterministic behavior: no randomness; results rely solely on input and fixed heuristics."
        ],
        "strategy": {
            "overview": "A simple, interpretable pipeline that can be expanded later. Uses staged constructive improvements and constraint checks with deterministic tie-breaking.",
            "stages": [
                {
                    "name": "initial_construct",
                    "description": "Build a base tour by nearest-allowed-vertex greedy with deterministic tie-breaking.",
                    "details": [
                        "Maintain a visited set starting from a fixed start node (lowest index).",
                        "At each step, choose the nearest unvisited node that does not violate constraints if appended.",
                        "If multiple candidates are equally near, break ties by smallest index.",
                        "If no feasible next node exists, fall back to a simple path extension to the remaining nodes in index order that respects constraints."
                    ],
                    "constraints_handling": [
                        "Forbidden edges are respected.",
                        "Mandatory visit nodes (if any) must appear in the tour; ensure feasibility by inserting them when possible."
                    ]
                },
                {
                    "name": "local_improvement",
                    "description": "Apply simple 2-opt swaps that improve the tour while maintaining feasibility.",
                    "details": [
                        "Iterate over edge pairs (i, i+1) and (j, j+1) with i+1 < j, test swap (i,i+1) with (j,j+1) if it preserves feasibility.",
                        "Accept swap only if it reduces total length and respects constraints.",
                        "Deterministic evaluation order; stop after a fixed number of passes."
                    ],
                    "constraints_handling": [
                        "All constraints (forbidden edges, mandatory visits) remain satisfied after swap."
                    ]
                },
                {
                    "name": "feasibility_fix",
                    "description": "If the constructed tour violates constraints or cannot be completed, apply deterministic repair.",
                    "details": [
                        "If mandatory visits missing, insert them in the earliest feasible positions in index order.",
                        "If forbidden edges appear, perform a neighbor reassignment to avoid them while trying to keep path length reasonable."
                    ]
                }
            ]
        },
        "data_encoding": {
            "start_node": "0",
            "tiebreaker": "lowest_index",
            "representation": {
                "distance": "assumed to be provided as a full matrix or a function by the caller; this scaffold does not perform I/O.",
                "constraints": {
                    "forbidden_edges": "set of (i, j) tuples",
                    "mandatory_visits": "set of node indices that must appear",
                    "capacity_constraints": "optional; not enforced by default"
                }
            }
        },
        "expected_outputs": {
            "tour": "list of node indices in visitation order forming a tour (implicitly closes back to start if desired).",
            "length": "total distance of the tour, computed deterministically from a provided distance function or matrix.",
            "status": "string label such as 'feasible' or 'infeasible' with notes on constraint handling."
        },
        "notes": [
            "This scaffold is deterministic and interpretable; it is suitable as a starting point for held-out TSPLIB and synthetic transfer evaluation.",
            "No external libraries or imports are required."
        ],
    }
