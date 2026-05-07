def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def mhd(a, b, c, d):  # manhattan
        return abs(a - c) + abs(b - d)

    if not resources:
        # Run to opposite corner relative to opponent to avoid sweep interception
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
    else:
        # Prefer resources we can reach sooner than opponent (anti-sweep)
        tx, ty = resources[0]
        best = None
        for rx, ry in resources:
            sd = mhd(sx, sy, rx, ry)
            od = mhd(ox, oy, rx, ry)
            # Prioritize positive lead; tie-break by shorter self distance
            lead = od - sd
            # Slight bias away from opponent row/col to avoid getting swept
            bias = -1 if (rx == ox or ry == oy) else 0
            key = (lead + bias, -sd, -(rx + ry))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    # If too close to opponent, temporarily prioritize distancing
    close = (mhd(sx, sy, ox, oy) <= 3)

    def cell_score(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        d_self = mhd(nx, ny, tx, ty)
        d_opp = mhd(nx, ny, ox, oy)
        # If close, emphasize distance; else emphasize reaching target before opponent
        if close:
            return (d_opp - d_self, d_opp, -d_self)
        else:
            return ((mhd(ox, oy, tx, ty) - (d_self + 0)) + (d_opp * 0.05), -d_self, d_opp)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = cell_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]