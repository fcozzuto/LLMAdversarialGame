def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [0, 0] if best is None else [best[1], best[2]]

    opp_center_bias = cheb(ox, oy, (w - 1) // 2, (h - 1) // 2)
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        our_adv = -10**9
        best_d1 = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            adv = (d2 - d1)
            if d1 < best_d1:
                best_d1 = d1
            if adv > our_adv:
                our_adv = adv
        # primary: deny opponent by increasing our advantage over their distance
        # secondary: minimize our distance to some resource
        # tertiary: slightly avoid letting opponent be "central" (encourages lateral moves)
        v = (our_adv * 100) - best_d1 - 0.05 * (cheb(nx, ny, (w - 1) // 2, (h - 1) // 2) - opp_center_bias)
        if best is None or v > best[0]:
            best = (v, dx, dy)
    return [0, 0] if best is None else [best[1], best[2]]