def choose_move(observation):
    # Deterministic balance: if there is a resource, move toward the closest; otherwise stay.
    x, y = observation["self_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    # Choose the resource with minimum Manhattan distance
    target = min(resources, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    dx = 0 if target[0] == x else (1 if target[0] > x else -1)
    dy = 0 if target[1] == y else (1 if target[1] > y else -1)
    return [dx, dy]