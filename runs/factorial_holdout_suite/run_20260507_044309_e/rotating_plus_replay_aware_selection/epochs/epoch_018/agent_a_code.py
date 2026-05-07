def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    # Target selection: prefer resources we can reach earlier; tie-break by center proximity.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we can arrive earlier, strongly prefer; otherwise, still consider but reduce score.
        lead = do - ds  # positive => we are earlier
        center_bias = cheb(rx, ry, cx, cy)
        key = (-lead, center_bias, rx, ry)  # deterministic tiebreak
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no valid resources, drift toward center while avoiding obstacles.
    tx, ty = best if best is not None else (cx, cy)

    # Move toward chosen target using greedy one-step score.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Encourage decreasing distance to target; slightly discourage staying if moves improve.
        d = cheb(nx, ny, tx, ty)
        d0 = cheb(sx, sy, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)  # slight safety pressure
        val = (d, d0 - d, -opp_d, dx, dy)  # lexicographic deterministic
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]