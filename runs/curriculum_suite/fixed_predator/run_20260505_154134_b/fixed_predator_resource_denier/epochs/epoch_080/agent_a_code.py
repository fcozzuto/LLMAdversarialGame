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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, cx, cy)
            t = cheb(nx, ny, ox, oy)
            key = (-d, -t, nx, ny)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_move = (0, 0)
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_res_key = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer a resource where we are closer (opp_dist - self_dist high),
            # but still make progress to take it.
            rel = od - sd
            take = -sd
            # Slightly prefer resources closer to center (helps against deniers).
            center_bias = -cheb(rx, ry, cx, cy)
            res_key = (rel, take, center_bias, -rx, -ry)
            if best_res_key is None or res_key > best_res_key:
                best_res_key = res_key

        # Also keep move quality w.r.t. current opponent pressure.
        # If we can deny a resource (rel positive), we win tempo.
        # Otherwise, push toward a promising target.
        rel = best_res_key[0]
        sd_est = -best_res_key[1]
        opp_to_center = cheb(ox, oy, cx, cy)
        self_to_center = cheb(nx, ny, cx, cy)

        # Key: primary maximize denial/tempo, secondary go to target, tertiary reduce center drift.
        key = (rel, -sd_est, -(self_to_center - opp_to_center), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]