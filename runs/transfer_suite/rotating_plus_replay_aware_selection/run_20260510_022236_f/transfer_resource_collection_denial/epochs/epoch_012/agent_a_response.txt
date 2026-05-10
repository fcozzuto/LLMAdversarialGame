def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def move_to(tx, ty):
        best = None
        bx, by = sx, sy
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = bx + dx, by + dy
                if not inb(nx, ny):
                    continue
                if (nx, ny) in obs_set:
                    continue
                d = cheb(nx, ny, tx, ty)
                # deterministic tie-break: prefer staying close to dx,dy ordering then lower dx then dy
                cand = (d, abs(dx), abs(dy), dx, dy)
                if best is None or cand < best:
                    best = cand
                    best_move = (dx, dy)
        if best is None:
            return [0, 0]
        return [best_move[0], best_move[1]]

    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are not clearly behind; if denier, sometimes contest when only slightly behind.
        behind = opd - myd
        # lead_flag: 1 if we're too far behind, else 0 (minimize)
        lead_flag = 1 if myd > opd + 1 else 0
        key = (lead_flag, behind if behind > 0 else 0, myd, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    return move_to(rx, ry)