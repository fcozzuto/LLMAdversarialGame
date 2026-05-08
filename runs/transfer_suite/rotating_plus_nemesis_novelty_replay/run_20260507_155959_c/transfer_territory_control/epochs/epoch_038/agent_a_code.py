def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            if p is not None and len(p) >= 2:
                obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    opp_cells = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    candidates = []
    best_cell = None
    best_adv = -10**18
    for c in unclaimed:
        if not c or len(c) < 2: 
            continue
        x, y = int(c[0]), int(c[1])
        if not free(x, y) or (x, y) in opp_cells:
            continue
        dself = md(sx, sy, x, y)
        dopp = md(ox, oy, x, y)
        adv = dopp - dself
        if adv > best_adv:
            best_adv, best_cell = adv, (x, y)

    # If no useful unclaimed, prefer expanding away from opponent and toward center.
    if best_cell is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = -10**18
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = md(nx, ny, ox, oy) - md(nx, ny, tx, ty)
            if score > best:
                best, best_move = score, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_cell
    best = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = (md(ox, oy, tx, ty) - md(nx, ny, tx, ty))
        # small tie-break: closer to target
        score -= 0.001 * md(nx, ny, tx, ty)
        if score > best:
            best, best_move = score, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]