def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    ti = int(observation.get("turn_index", 0) or 0)
    center = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive means we arrive earlier
        # tie-break favors earlier arrival, then closer-to-center, then stable parity
        cx, cy = center
        dc = abs(rx - cx) + abs(ry - cy)
        key = (-advantage, ds, dc, ((rx + ry + ti) & 1))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministic sidestep: prefer a move that keeps chebyshev distance smallest to target.
        best_step = [0, 0]
        best_dist = 10**9
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                if mx == 0 and my == 0:
                    pass
                px, py = sx + mx, sy + my
                if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                    d = cheb(px, py, tx, ty)
                    if d < best_dist or (d == best_dist and (mx != 0 or my != 0) and (((mx*3+my+ti) & 1) == 0)):
                        best_dist = d
                        best_step = [mx, my]
        return best_step
    return [dx, dy]