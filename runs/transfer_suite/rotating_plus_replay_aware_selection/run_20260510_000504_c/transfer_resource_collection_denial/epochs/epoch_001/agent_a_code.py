def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # deterministic fallback: move toward center (3.5,3.5) in steps
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in ((0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick a resource prioritizing where we can beat opponent to it.
    best_r = None
    for rx, ry in resources:
        d_s = dsq(sx, sy, rx, ry)
        d_o = dsq(ox, oy, rx, ry)
        key = (d_s - d_o, d_s, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, (rx, ry))
    tx, ty = best_r[1]
    cur_op = dsq(ox, oy, tx, ty)

    deltas = ((0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1))
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d_new = dsq(nx, ny, tx, ty)
        d_opp_new = cur_op  # opponent move unknown; approximate with current
        # Move score: prioritize reaching target sooner; slight bias toward making distance advantage.
        score = (-d_new, (d_new - d_opp_new), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_m is None or score < best_m[0]:
            best_m = (score, dx, dy)
    return [best_m[1], best_m[2]] if best_m else [0, 0]