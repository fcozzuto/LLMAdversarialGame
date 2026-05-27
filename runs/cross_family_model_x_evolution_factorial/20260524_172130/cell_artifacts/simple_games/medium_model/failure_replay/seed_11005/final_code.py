def choose_move(observation):
    # Defensive extraction with defaults
    x = observation.get("player_x", observation.get("x", 0))
    y = observation.get("player_y", observation.get("y", 0))

    candidates = []

    # Gather plausible targets defensively
    for key_pair in [
        ("resource_x", "resource_y"),
        ("evader_x", "evader_y"),
        ("opponent_x", "opponent_y"),
        ("beacon_x", "beacon_y"),
        ("goal_x", "goal_y"),
        ("target_x", "target_y"),
    ]:
        rx = observation.get(key_pair[0])
        ry = observation.get(key_pair[1])
        if rx is not None and ry is not None:
            candidates.append((rx, ry))

    # If any candidates, choose nearest in Manhattan distance
    target = None
    best_dist = None
    for tx, ty in candidates:
        if tx is None or ty is None:
            continue
        dist = abs(tx - x) + abs(ty - y)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            target = (tx, ty)

    if target is not None:
        tx, ty = target
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    # Fallback: move toward origin to stay defensive if no target
    if x != 0 or y != 0:
        dx = -1 if x > 0 else (1 if x < 0 else 0)
        dy = -1 if y > 0 else (1 if y < 0 else 0)
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    # Default to top-left move
    return [-1, -1]
