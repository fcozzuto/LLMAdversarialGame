def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if resources:
            best = None
            for x, y in resources:
                ds = cheb(sx, sy, x, y)
                do = cheb(ox, oy, x, y)
                # Prefer resources we can reach no later than opponent; else fall back to nearest.
                cand = (0 if ds <= do else 1, ds, -do, x, y)
                if best is None or cand < best[0]:
                    best = (cand, (x, y))
            return best[1]
        # No resources: go toward our farthest-from-opponent corner deterministically.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corners = [c for c in corners if ok(c[0], c[1])]
        target = None
        for x, y in corners or [(sx, sy)]:
            score = (cheb(ox, oy, x, y), -cheb(sx, sy, x, y), x, y)
            if target is None or score > target[0]:
                target = (score, (x, y))
        return target[1] if target else (sx, sy)

    tx, ty = best_target()
    bd = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Primary: get closer to target. Secondary: prevent opponent from being closer.
        cand = (ds2, 0 if cheb(ox, oy, tx, ty) >= ds2 else 1, -do2, nx, ny)
        if bd is None or cand < bd:
            bd = cand
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]