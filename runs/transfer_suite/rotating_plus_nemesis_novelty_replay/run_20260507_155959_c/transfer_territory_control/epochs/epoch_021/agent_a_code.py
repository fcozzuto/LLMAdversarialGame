def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed = [(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles]
    if not unclaimed:
        return [0, 0]

    # Target: nearest unclaimed cell, with slight bias to those closer to center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_t = None
    best_key = None
    for x, y in unclaimed:
        key = (abs(x - sx) + abs(y - sy), abs(x - cx) + abs(y - cy))
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)
    tx, ty = best_t

    # Prefer a move that approaches target and is not blocked by obstacle.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Heuristic: closer to target; bonus for entering unclaimed; bonus for flipping opponent territory.
        d = abs(nx - tx) + abs(ny - ty)
        in_unclaimed = 1 if (nx, ny) in set(unclaimed) else 0
        flip_bonus = 1 if (nx, ny) in opp_cells else 0
        in_self = 1 if (nx, ny) in self_cells else 0
        key = (d, -in_unclaimed, -flip_bonus, -in_self, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]