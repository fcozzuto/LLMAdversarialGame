def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", None)
    if resources is None:
        resources = []
    targets = []
    for r in resources or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not valid(sx, sy):
        return [0, 0]

    def best_step(tx, ty):
        best = None
        best_sc = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            sc = d * 10
            sc += 0 if (nx, ny) == (ox, oy) else (abs(nx - ox) + abs(ny - oy))
            if best_sc is None or sc < best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        return best if best is not None else (0, 0)

    if targets:
        bestx = targets[0][0]
        besty = targets[0][1]
        bestd = abs(sx - bestx) + abs(sy - besty)
        for tx, ty in targets[1:]:
            d = abs(sx - tx) + abs(sy - ty)
            if d < bestd or (d == bestd and (tx, ty) < (bestx, besty)):
                bestd = d
                bestx, besty = tx, ty
        return list(best_step(bestx, besty))

    if sx == ox and sy == oy:
        return [0, 0]

    return list(best_step(ox, oy))