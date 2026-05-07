def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a "race target": prefer resources we can reach before opponent; otherwise minimize being behind.
    best_r = resources[0]
    best_sc = -10**18
    for rx, ry in resources:
        sdist = man(sx, sy, rx, ry)
        odist = man(ox, oy, rx, ry)
        ahead = odist - sdist  # positive => we are closer
        # Strongly prioritize being ahead; if tied/behind, still go for smaller sdist to keep tempo.
        sc = ahead * 1000 - sdist
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r
    # Candidate move: greedily minimize our distance to chosen target, with mild preference to keep moving (avoid idle).
    best_move = [0, 0]
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        val = man(nx, ny, rx, ry)
        if dx == 0 and dy == 0:
            val += 0.5  # deterministic tie-break: avoid staying if possible
        # If we move into a square adjacent to an obstacle, slightly penalize to reduce clogging.
        adj_pen = 0
        for ox2, oy2 in obstacles:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                adj_pen = 0.25
                break
        val += adj_pen
        if val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move