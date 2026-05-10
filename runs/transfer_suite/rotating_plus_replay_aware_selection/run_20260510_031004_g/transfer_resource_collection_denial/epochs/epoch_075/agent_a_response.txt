def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def cell_blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        race = opp_d - my_d  # positive means I'm earlier (or tied/less delayed)
        # Tie-break: prefer "higher" coords (deterministic) and closer to center once race is good.
        center_bias = -(abs(rx - cx) + abs(ry - cy)) * 0.01
        coord_bias = (ry * 0.001) + (rx * 0.0001)
        # Strongly commit when I'm not behind; otherwise still pursue but reduce.
        score = (race * 100.0) + center_bias + coord_bias - (0.02 * my_d)
        # Deterministic tie-break
        key = (score, -ry, -rx, my_d, opp_d)
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    # Deterministic obstacle-aware fallback: try alternative single-axis steps toward target.
    if dx != 0 and dy != 0:
        candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not cell_blocked(nx, ny):
            return [int(mx), int(my)]
    return [0, 0]