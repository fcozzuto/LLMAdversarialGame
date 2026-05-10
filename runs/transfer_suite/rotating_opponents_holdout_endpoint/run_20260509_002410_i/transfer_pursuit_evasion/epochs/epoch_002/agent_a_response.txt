def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    obstacles = observation.get("obstacles", [])
    obs = set((int(a), int(b)) for a, b in obstacles)

    my_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursuer" in my_role) or ("pursue" in my_role)

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    def d2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    candidates = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        dist_sq = d2(nx, ny, ox, oy)
        if is_pursuer:
            # Minimize distance to opponent; deterministic tie-breaks
            corner_further = max(d2(nx, ny, cx, cy) for cx, cy in corners)
            key = (dist_sq, -corner_further, abs(nx - w // 2) + abs(ny - h // 2), dx, dy)
        else:
            # Maximize distance from opponent; head for farthest corner
            corner_best = max(d2(nx, ny, cx, cy) for cx, cy in corners)
            key = (-dist_sq, -corner_best, abs(nx - w // 2) + abs(ny - h // 2), -dx, -dy)
        if best is None or key < best_key:
            best, best_key = (dx, dy), key

    return [int(best[0]), int(best[1])]