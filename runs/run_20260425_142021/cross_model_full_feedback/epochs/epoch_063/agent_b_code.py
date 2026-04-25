def choose_move(observation):
    # Deterministic strategy: move toward the closest resource using Manhattan distance.
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]