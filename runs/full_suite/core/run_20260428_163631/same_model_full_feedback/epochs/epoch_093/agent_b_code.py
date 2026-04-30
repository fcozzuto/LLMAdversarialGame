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
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if (sx, sy) in res_set:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (md - od, md, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            md = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer moves that approach target and improve relative race; deterministic tiebreakers
            candidates.append(((md - od, md, nx, ny), dx, dy))
    candidates.sort(key=lambda t: t[0])
    return [int(candidates[0][1]), int(candidates[0][2])]