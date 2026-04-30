def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if resources:
        best_t = None
        best_adv = None
        for rx, ry in resources:
            ds = d2(sx, sy, rx, ry)
            do = d2(ox, oy, rx, ry)
            adv = ds - do  # smaller => relatively closer to us
            if best_adv is None or adv < best_adv or (adv == best_adv and (ds < d2(sx, sy, best_t[0], best_t[1]))):
                best_adv = adv
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx = (w - 1) // 2
        ty = (h - 1) // 2

    opp_dist_pen = d2(ox, oy, tx, ty)
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds = d2(nx, ny, tx, ty)
        dso = d2(ox, oy, tx, ty)
        block = 0
        # small penalty if we move closer to opponent while we pursue
        opp_close = d2(nx, ny, ox, oy)
        val = ds + 0.001 * (opp_close) + 0.0001 * (opp_dist_pen - dso)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]