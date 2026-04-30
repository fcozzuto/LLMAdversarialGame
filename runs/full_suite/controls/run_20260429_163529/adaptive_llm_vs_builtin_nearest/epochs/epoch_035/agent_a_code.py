def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Pick resource: prefer ones we can reach sooner than opponent; bias toward central.
    best = None
    best_key = None
    for (rx, ry) in res:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Maximize lead => minimize (d_me - 0.6*d_op). Also prefer central resources slightly.
        lead_cost = d_me - 0.6 * d_op
        center_bias = abs(rx - cx) + abs(ry - cy)
        key = (lead_cost, center_bias, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    # Choose one-step move minimizing estimated cost toward target while avoiding obstacles.
    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1),
              (-1, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to = cheb(nx, ny, tx, ty)

        # Additional deterministic shaping: don't step into "opponent pressure" (cells closer to opp than us by too much).
        d_opp_here = cheb(ox, oy, nx, ny)
        d_us_here = cheb(nx, ny, tx, ty)
        pressure = max(0, d_opp_here - d_us_here)

        # Keep moving: slight cost for staying.
        stay_pen = 0.2 if (dx == 0 and dy == 0) else 0.0
        # Prefer not increasing distance to target.
        inc_pen = 0.15 if d_to > cheb(sx, sy, tx, ty) else 0.0

        val = d_to + 0.25 * pressure + stay_pen + inc_pen
        if best_val is None or val < best_val - 1e-9 or (abs(val - best_val) <= 1e-9 and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]