def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_margin(px, py):
        if not resources:
            return 0, None
        best = -10**18
        best_r = None
        for (rx, ry) in resources:
            d_us = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            margin = d_op - d_us
            if margin > best:
                best = margin
                best_r = (rx, ry)
        return best, best_r

    def value_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        margin, target = best_margin(nx, ny)
        if not target:
            tx, ty = (w - 1) if sx <= (w - 1) // 2 else 0, (h - 1) if sy <= (h - 1) // 2 else 0
            dist = cheb(nx, ny, tx, ty)
            return -dist
        rx, ry = target
        d_us = cheb(nx, ny, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer immediate contest and proximity; reward reducing opponent's advantage
        return margin * 1000 - d_us + (d_op - d_us)

    # Deterministic tie-breaker order by a fixed preference vector
    pref = {(0, 0): 0, (1, 1): 1, (1, 0): 2, (0, 1): 3, (-1, 1): 4, (-1, 0): 5, (0, -1): 6, (1, -1): 7, (-1, -1): 8}
    bestv = -10**30
    bestm = (0, 0)
    for dx, dy in moves:
        v = value_for_move(dx, dy)
        key = (v, -pref[(dx, dy)])
        if key > (bestv, -pref[bestm]):
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]