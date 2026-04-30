def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources or (sx, sy) in obstacles:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center_score(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        if dx < 0: dx = -dx
        dy = y - cy
        if dy < 0: dy = -dy
        return dx + dy

    # Choose resource that we can reach earlier than opponent, preferring larger lead.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        # Higher lead, then smaller my distance, then closer to center (tie-break deterministic)
        key = (lead, -myd, -center_score(rx, ry), rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    # Deterministic preference: reduce chebyshev distance; avoid obstacles.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        md = cheb(nx, ny, tx, ty)
        # Prefer moves that also increase opponent distance to the target slightly.
        od = cheb(ox, oy, tx, ty)
        new_od = od
        mkey = (-md, -(new_od - cheb(ox, oy, nx, ny)), -abs((tx - nx)) - abs((ty - ny)), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]