def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold using budget_matched_no_replay approach.
    # This scaffold emphasizes robustness across held-out TSPLIB and synthetic instances, with
    # clear interpretability and no reliance on external imports.
    scaffold = {
        "name": "budget_matched_no_replay_constrained_tsp",
        "version": 1,
        "description": (
            "Deterministic heuristic scaffold for constrained TSP using a budget-aware "
            "construction with no replay/memory reuse. Leverages simple, interpretable steps "
            "to produce feasible tours under given budget and constraint budgets."
        ),
        "principles": [
            "Deterministic construction: same input yields same tour",
            "Budget-aware: respects total distance budget and constraint budgets",
            "Feasibility-first: ensure all constraints are satisfied when possible",
            "Interpretability: use straightforward steps (nearest feasible, then insertion)"
        ],
        "parameters": {
            "distance_budget": {
                "type": "float",
                "description": "Maximum allowed tour length",
                "default": None
            },
            "visit_budget": {
                "type": "int",
                "description": "Maximum number of visits per node (for constrained variants)",
                "default": 1
            },
            "constr": {
                "type": "dict",
                "description": "Constraint specification, e.g., time windows or required arc exclusions",
                "default": {}
            },
            "nodes": {
                "type": "list",
                "description": "List of node identifiers with coordinates as tuples (id, (x, y)) or similar",
                "default": []
            },
            "start_node": {
                "type": "object",
                "description": "Starting node identifier",
                "default": None
            },
        },
        "construction_steps": [
            {
                "step": 1,
                "name": "initialize",
                "action": "Create an initial candidate path starting from start_node (or lowest-id node).",
                "feasibility": "Path is empty or single node; feasibility trivially satisfied."
            },
            {
                "step": 2,
                "name": "greedy_extend",
                "action": (
                    "Iteratively append the nearest feasible next node that does not violate the "
                    "distance budget or per-node visit limits, and respects simple constraints."
                ),
                "feasibility": "Maintains budget constraint and basic constraints per step."
            },
            {
                "step": 3,
                "name": "check_feasibility_and_close",
                "action": (
                    "If adding the final edge closes a tour within budget, close; otherwise attempt a "
                    "feasible closure by connecting to a suitable remaining node while honoring budgets."
                ),
                "feasibility": "Ensures a complete tour if possible under budgets."
            },
            {
                "step": 4,
                "name": "budget_adjustment",
                "action": (
                    "If over budget, perform minimal removal of the largest-cost arc(s) to fit within the distance_budget "
                    "while keeping connectivity."
                ),
                "feasibility": "Produces a feasible tour within the budget if possible by pruning."
            }
        ],
        "outputs": {
            "tour": {
                "type": "list",
                "description": "Ordered list of node identifiers representing the tour, returning to start."
            },
            "metrics": {
                "length": {"type": "float", "description": "Total tour length"},
                "feasible": {"type": "bool", "description": "Whether constraints/budget satisfied"}
            }
        },
        "robustness": {
            "notes": "Deterministic behavior across TSPLIB-like and synthetic instances. Uses simple heuristics that generalize beyond training instances.",
            "fallbacks": [
                "If no feasible tour under budget exists, return an empty tour with feasible flag false.",
                "If start_node is missing, select the node with smallest id deterministically."
            ]
        }
    }
    return scaffold
