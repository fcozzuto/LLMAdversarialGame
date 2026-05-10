def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role)
    if not is_pursuer and not is_evader:
        is_pursuer = True

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in ob:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dxdy = candidates[0][2:]
    best_val = None

    for nx, ny, dx, dy in candidates:
        d = manhattan(nx, ny, ox, oy)
        center = abs(nx - cx) + abs(ny - cy)

        # Local obstacle awareness: avoid positions with too many blocked neighbors (dead-ends).
        blocked_neighbors = 0
        for ex, ey, _, _ in candidates:
            pass
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if not in_bounds(tx, ty) or (tx, ty) in ob:
                blocked_neighbors += 1

        if is_pursuer:
            # Prefer smaller distance; avoid tight dead-ends; slightly prefer center for maneuverability.
            val = d * 10.0 + blocked_neighbors * 0.35 + center * 0.01
            better = (best_val is None) or (val < best_val)
        else:
            # Prefer larger distance; avoid being boxed in; slightly prefer center to prevent corner trap.
            val = -d * 10.0 + blocked_neighbors * 0.55 + center * 0.01
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]