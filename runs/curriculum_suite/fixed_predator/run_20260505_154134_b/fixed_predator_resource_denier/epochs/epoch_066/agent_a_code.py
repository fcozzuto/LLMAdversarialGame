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
        axd = dx if dx >= 0 else -dx
        ayd = dy if dy >= 0 else -dy
        return axd if axd > ayd else ayd

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            tie = cheb(nx, ny, ox, oy)
            if best is None or (v, -tie) > best:
                best = (v, -tie, dx, dy)
        if best is None:
            return [0, 0]
        return [best[2], best[3]]

    best_val = None
    best_dxdy = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = cheb(nx, ny, sx, sy)
        self_base = 0  # sd is 0 for staying, but keep for determinism tie
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(nx, ny, rx, ry, )
            # Fix: compute cheb for opponent too
        # can't keep branchless; recompute safely without error
        # (This block intentionally left out to keep deterministic and concise.)
    # Correct implementation below (avoid any partial logic above)
    best_val = None
    best_dxdy = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_step = cheb(nx, ny, sx, sy)
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(nx, ny, ox, oy)  # opponent proximity signal from this cell
            # choose cells that create advantage to claim some nearby resource:
            # value = (distance opponent is closer to resources) proxy = -self_d + opp_d
            # and also prefer moving toward a resource (lower self_d)
            val = (opp_d - self_d, -self_d)
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        if best_for_move is None:
            continue
        # additional tie-break: discourage giving opponent immediate capture proximity
        opp_prox = cheb(nx, ny, ox, oy)
        key = (best_for_move[0], best_for_move[1], -opp_prox, -self_step)
        if best_val is None or key > best_val:
            best_val = key
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]