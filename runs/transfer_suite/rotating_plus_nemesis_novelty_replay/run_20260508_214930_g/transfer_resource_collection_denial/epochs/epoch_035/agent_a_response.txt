def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res_set.add((x, y))
    if (sx, sy) in res_set:
        return [0, 0]
    if not res_set:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_r = None
    best_sc = None
    for rx, ry in res_set:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        lead = oppd - myd  # positive if we arrive first or at same time
        center = - (abs(rx - cx) + abs(ry - cy))  # prefer center-ish deterministically
        sc = lead * 20 - myd + center * 0.01
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_mv_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving toward target while also improving "arrive-first" potential
        d_to_t = cheb(nx, ny, tx, ty)
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        lead = oppd - myd
        sc = lead * 10 - d_to_t
        if best_mv_sc is None or sc > best_mv_sc:
            best_mv_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]