def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res_raw = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_raw if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    resources = [(p[0], p[1]) for p in res_raw if p and len(p) >= 2]

    # If no resources known, run to center-ish while keeping distance from opponent
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cheb(nx, ny, w // 2, h // 2) - cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = None
    bestv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Strongly prefer resources where we are closer than opponent; otherwise pick closest with penalty.
        v = (opd - myd) * 1000 - myd * 5 + cheb(rx, ry, w - 1, h - 1) * 0 + (rx + ry) * 0
        # Small deterministic tie-break: prefer lower (rx,ry)
        if best_target is None or v > bestv or (v == bestv and (rx, ry) < best_target):
            bestv = v
            best_target = (rx, ry)

    tx, ty = best_target
    # Greedy step toward target, but allow staying if all safe moves worsen.
    curd = cheb(sx, sy, tx, ty)
    best = [0, 0]
    best_step_v = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Encourage moves that reduce distance to target and also don't let opponent gain too much on it.
        opd_next = cheb(ox, oy, tx, ty)
        v = (curd - nd) * 1000 - nd * 3 + (opd_next - nd) * 10
        # Deterministic tie-break: choose lexicographically smallest (dx,dy) among equals
        if v > best_step_v or (v == best_step_v and (dx, dy) < tuple(best)):
            best_step_v = v
            best = [dx, dy]
    return best