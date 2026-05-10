def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in ob:
            candidates.append((nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_score(x, y):
        # tie-break: avoid hugging corners too long when evading
        return abs(x - cx) + abs(y - cy)

    def mobility(x, y):
        m = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                m += 1
        return m

    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)
    # If role is unclear, infer by score intent: default to evader-like distance maximization (safer)
    if not pursuer and not ("evader" in role):
        pursuer = False

    best_dxdy = candidates[0][2:]
    best_key = None

    for nx, ny, dx, dy in candidates:
        dist = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # winning move if pursuer can step onto evader exactly
        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        if pursuer:
            # chase: minimize distance; if equal, prefer lower mobility for opponent capture pressure,
            # while avoiding moves that drastically reduce our own mobility.
            key = (dist, -mob, center_score(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key, best_dxdy = key, [dx, dy]
        else:
            # evade: maximize distance; if equal, prefer higher mobility and away from center only as needed
            key = (-dist, -mob, center_score(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key, best_dxdy = key, [dx, dy]

    return best_dxdy