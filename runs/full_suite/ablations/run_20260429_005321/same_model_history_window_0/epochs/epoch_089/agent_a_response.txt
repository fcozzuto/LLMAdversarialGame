def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if resources:
        target = min(resources, key=lambda p: dist2((sx, sy), p))
    else:
        target = (w // 2, h // 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    # Later in game, bias more toward defense (avoid opponent) if not making progress.
    turn = observation.get("turn_index", 0)
    defense_weight = 0.15 if turn > 40 else 0.05

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist2((nx, ny), target)
        oldd = dist2((sx, sy), target)
        oppd = dist2((nx, ny), (ox, oy))
        # Prefer moves that reduce distance to target; tie-break with opponent separation.
        progress = (oldd - myd)
        val = progress * 10.0 + oppd * defense_weight - myd * 0.01
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif val == best_val and (dx, dy) == (0, 0):
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]