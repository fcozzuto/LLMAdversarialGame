def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = str(observation.get("self_role", ""))
    opponent_role = str(observation.get("opponent_role", ""))
    pursuer = ("pursuer" in self_role.lower()) or ("pursuer" in opponent_role.lower() and "evader" in self_role.lower())
    if "evader" in self_role.lower() and "pursuer" in opponent_role.lower():
        pursuer = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = [0, 0]
    best_val = -10**18 if pursuer else -10**18
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break order: cand already fixed

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d = manh(nx, ny, ox, oy)
        near_corner_from_us = min(manh(nx, ny, cx, cy) for cx, cy in corners)
        opp_corner_dist = min(manh(ox, oy, cx, cy) for cx, cy in corners)

        if pursuer:
            # minimize opponent distance; also try to "compress" by preferring moves that reduce opponent's escape corner distance proxy
            val = -d - 0.15 * opp_corner_dist - 0.03 * near_corner_from_us
        else:
            # maximize distance; avoid self getting too close to any corner
            val = d + 0.07 * near_corner_from_us

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best