def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def mdist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def nearest_obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000_000
        if not obstacles:
            return 0
        best = 10**9
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best: best = d
        if best <= 0: return 10_000_000
        if best == 1: return 1500
        if best == 2: return 250
        if best == 3: return 60
        return 0

    def corner_bias(x, y):
        # bias toward nearest corner for evader; opposite for pursuer
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bc = min(mdist(x, y, cx, cy) for cx, cy in corners)
        return -bc if not pursuer else bc

    best_mv, best_sc = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):  # deterministic reject: skip invalid
            continue
        d = mdist(nx, ny, ox, oy)
        pen = nearest_obs_pen(nx, ny)
        ax = abs(nx - ox)
        ay = abs(ny - oy)
        diag_align = -(ax + ay) if pursuer else (ax + ay)
        sc = 0
        if pursuer:
            sc = (-d) * 100 + diag_align * 0.5 + corner_bias(nx, ny) * 0.1 - pen
        else:
            sc = (d) * 100 + diag_align * 0.5 + corner_bias(nx, ny) * 0.1 - pen
        if sc > best_sc:
            best_sc, best_mv = sc, [dx, dy]

    # If all moves were invalid (shouldn't happen), stay.
    return best_mv if best_mv else [0, 0]