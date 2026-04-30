def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    # Pick a target resource (ignore if already on one)
    res = []
    for rx, ry in resources:
        if rx == sx and ry == sy:
            continue
        res.append((rx, ry))
    if not res:
        # If none left/available, drift toward center to reduce chance of being stuck
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in res:
            d = max(abs(rx - sx), abs(ry - sy))
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Evaluate candidate moves
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            dist_target = max(abs(tx - nx), abs(ty - ny))
            # Prefer not to move toward opponent too aggressively (tie-break only)
            dist_opp = max(abs(ox - nx), abs(oy - ny))
            # Lower is better; add small preference for moving (avoid too much staying still)
            move_cost = (dx == 0 and dy == 0)
            score = (dist_target, -dist_opp, move_cost, abs(tx - nx) + abs(ty - ny), dx, dy)
            candidates.append((score, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])

    # Deterministic tie-break: also prefer diagonal if equal score, then smaller dx, then smaller dy
    best_score, best_move = candidates[0][0], candidates[0][1]
    return best_move