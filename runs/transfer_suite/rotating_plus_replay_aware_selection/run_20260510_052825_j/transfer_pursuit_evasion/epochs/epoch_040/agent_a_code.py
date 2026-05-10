def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    evade = ("evad" in self_role) or (self_role == "evader") or ("evad" in opponent_role) or (opponent_role == "evader" and "purs" in self_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def neigh_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        free = neigh_count(nx, ny)
        # If evading: prioritize distance; penalize low-mobility squares and "shadowing" (moving closer in both coords).
        # If pursuing: prioritize reducing distance; prefer positions with mobility to keep chasing.
        if evade:
            score = (d * 1000) + (free * 5) - ((abs(nx - ox) < abs(sx - ox)) and (abs(ny - oy) < abs(sy - oy)) and 20 or 0)
        else:
            score = (-d * 1000) + (free * 5) + ((abs(nx - ox) < abs(sx - ox)) or (abs(ny - oy) < abs(sy - oy)) ) * 10
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then nearer to center.
        tie = (-abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        key = (score, tie, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]