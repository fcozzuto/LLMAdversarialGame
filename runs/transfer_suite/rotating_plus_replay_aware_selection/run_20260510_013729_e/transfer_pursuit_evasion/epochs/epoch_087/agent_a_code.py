def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        resources = None

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    if resources:
        tx, ty = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        evade = opd <= myd
        targetx, targety = (sx, sy) if evade else (tx, ty)
    else:
        evade = cheb(sx, sy, ox, oy) <= max(1, min(w, h) // 3)
        targetx, targety = (sx, sy) if evade else (w // 2, h // 2)

    def score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            d_to_target = cheb(nx, ny, targetx, targety)
            d_from_opp = cheb(nx, ny, ox, oy)
            if evade:
                return d_from_opp - d_to_target * 0.1
            return -d_to_target + d_from_opp * 0.05
        d_from_opp = cheb(nx, ny, ox, oy)
        d_to_center = cheb(nx, ny, targetx, targety)
        if evade:
            return d_from_opp - d_to_center * 0.1
        return -d_to_center + d_from_opp * 0.05

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            sc = score(nx, ny)
            if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best):
                best_score = sc
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]