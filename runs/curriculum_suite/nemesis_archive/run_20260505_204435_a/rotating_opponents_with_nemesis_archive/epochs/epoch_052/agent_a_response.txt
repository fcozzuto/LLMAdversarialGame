def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if legal(x, y):
            rpos.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # If no resources, drift toward center while avoiding obstacles
    if not rpos:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            cand = (sc, nx, ny)
            if best is None or cand < best:
                best = cand
        return [best[1] - sx, best[2] - sy] if best else [0, 0]

    # Choose resource to intercept: maximize (opp_dist - self_dist), tie-break by self_dist then coord
    best_r = None
    best_key = None
    for x, y in rpos:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        gap = od - sd
        key = (-gap, sd, x, y)  # smallest is best: prioritize larger gap (so -gap smallest)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (x, y)

    tx, ty = best_r

    # Pick move that reduces distance to target; if blocked, choose best safe alternative
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd = md(nx, ny, tx, ty)
        # small penalty if moving closer to opponent could help prevent getting out-competed
        od = md(nx, ny, ox, oy)
        sc = (sd, -od, nx, ny)
        if best is None or sc < best:
            best = sc

    if best is None:
        return [0, 0]
    nx, ny = best[2], best[3]
    return [nx - sx, ny - sy]