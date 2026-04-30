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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    cx, cy = w // 2, h // 2

    cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    def best_value(nx, ny):
        if resources:
            best = -10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources where we have advantage, and move toward them quickly.
                val = (od - sd) * 10 - sd
                # Slightly prefer keeping some distance from opponent.
                val -= 0.1 * cheb(nx, ny, ox, oy)
                if val > best:
                    best = val
            return best
        # No resources: go toward center, avoid opponent somewhat.
        return -cheb(nx, ny, cx, cy) - 0.05 * cheb(nx, ny, ox, oy)

    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in cands:
        v = best_value(nx, ny)
        # Deterministic tie-break: lexicographic order on (v, dx, dy) with higher v.
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]