def build_heuristic():
    return {
        'name': 'budget_matched_no_replay_candidate_1',
        'technique': 'budget_matched_no_replay',
        'description': 'A deterministic heuristic for constrained TSP focusing on budget matching with no replay or failure memory, using a straightforward greedy approach.',
        'parameters': {
            'initial_node_selection': 'nearest_neighbor',  # Start from the closest node to a predefined start (or arbitrary node)
            'edge_selection_criteria': 'cost_sorted',     # Sort candidate edges by cost
            'budget_allocation': 'equal_split',           # Split total budget evenly among selected edges
            'heuristic_step': 'greedy_extension',         # Extend the path greedily without backtracking
            'termination_condition': 'all_nodes_visited_or_budget_exhausted',
            'node_selection_strategy': 'closest_unvisited',  # Always pick the nearest unvisited node
            'edge_choice_policy': 'minimal_cost_within_budget'  # Select minimal cost edge within remaining budget
        },
        'robustness': 'designed to perform well across TSPLIB and synthetic instances, emphasizing interpretability and consistent heuristic behavior.',
        'heuristic_overview': 'Selects the next node as the nearest unvisited node within remaining budget until all nodes are visited or budget is exhausted, resulting in a feasible constrained TSP route.',
        'notes': 'This heuristic refrains from replay, failure memory, or compression components, and relies solely on deterministic greedy extensions based on cost and budget constraints.'
    }

