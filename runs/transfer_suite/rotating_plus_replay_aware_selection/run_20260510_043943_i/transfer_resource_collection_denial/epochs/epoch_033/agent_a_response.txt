def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        # Drift toward center to reduce being trapped
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    # Consider only a few resources to keep deterministic and fast
    resources_sorted = sorted(resources, key=lambda p: man(ox, oy, p[0], p[1]))
    top = resources_sorted[:5]

    def score_cell(x, y):
        best = -10**18
        for rx, ry in top:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            time_adv = do - ds  # positive is good for us
            # Prefer resources we can reach strictly earlier; still allow ties but penalize.
            contested = 1 if do <= ds else 0
            s = time_adv * 1000 - ds * 3 - contested * 200
            best = s if s > best else best
        # Mild incentive to keep moving toward a promising resource
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        val = score_cell(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move