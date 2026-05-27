def build_heuristic():
    return {
        'name': 'budget_matched_no_replay',
        'description': 'A straightforward heuristic for the constrained TSP, matching a predefined budget without replay or failure memory.',
        'parameters': {
            'budget': 1000,  # fixed tour length budget
            'initial_selection': 'nearest_neighbor',  # strategy for initial node selection
            'tour_extension_method': 'greedy_cost_insertion',  # method for extending the tour
            'max_iterations': 10000,  # maximum iterations to attempt
            'termination_condition': 'budget_exceeded',  # terminate once budget exceeded
        },
        'heuristic_steps': [
            'Initialize tour with a start node chosen by nearest neighbor heuristic.',
            'Iteratively extend the tour by selecting the closest feasible node not yet visited, respecting the budget limit.',
            'Use greedy cost-insertion to insert nodes into the current tour to minimize incremental cost.',
            'Terminate when no further feasible insertions remain within the budget constraints.',
            'Return the constructed tour as the heuristic solution.',
        ],
        'robustness_notes': (
            'Designed to perform well across TSPLIB instances and synthetic datasets by '
            'emphasizing deterministic greedy extension within a fixed budget, avoiding probabilistic or reloading strategies.'
        ),
        'interpretability': 'The heuristic uses simple nearest neighbor initialization and greedy insertion, making it transparent and easy to analyze.',
    }

