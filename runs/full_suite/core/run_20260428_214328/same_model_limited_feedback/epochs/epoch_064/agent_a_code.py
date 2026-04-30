def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((a, b) for a, b in obstacles)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set((r[0], r[1]) for r in resources)
    if (ox, oy) in res_set:
        return [0, 0]

    best = None
    best_adv = -10**9
    best_sd = 10**9
    for rx, ry in resources:
        sd = cheb(ox, oy, rx, ry)
        od = cheb(px, py, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best = (rx, ry)

    tx, ty = best
    dx_dir = 0 if tx == ox else (1 if tx > ox else -1)
    dy_dir = 0 if ty == oy else (1 if ty > oy else -1)

    candidates = [
        (dx_dir, dy_dir), (dx_dir, 0), (0, dy_dir),
        (dx_dir, -dy_dir), (-dx_dir, dy_dir), (-dx_dir, 0), (0, -dy_dir),
        (0, 0)
    ]
    candidates = [c for c in candidates if c != (0, 0)] + [(0, 0)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = ox + dx, oy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(px, py, tx, ty)
        val = (best_sd - nsd) * 100 - nsd + (nod - cheb(px, py, tx, ty)) * 0
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]