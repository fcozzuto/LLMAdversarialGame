def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return (0 <= nx < w) and (0 <= ny < h) and ((nx, ny) not in obstacles)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        if is_pursuer:
            # First: minimize distance; then prefer actions that don't immediately move onto opponent (distance=0 is worst anyway)
            val = (-dist, center_bias)
        else:
            # First: maximize distance; then stay closer to center a bit to avoid corner traps against zigzags
            val = (dist, center_bias)
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]