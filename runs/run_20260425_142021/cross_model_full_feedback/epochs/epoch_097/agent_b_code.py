def choose_move(observation):
    # Deterministic greedy move towards the nearest resource, with axis-aligned step.
    sx, sy = observation["self_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    # Choose the resource minimizing Manhattan distance
    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]