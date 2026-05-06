def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        nx, ny = x + dx, y + dy
        if free(nx, ny):
            return [dx, dy]
        nx, ny = x, y
        if free(x + dx, y):
            return [dx, 0]
        if free(x, y + dy):
            return [0, dy]
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if free(x + adx, y + ady):
                    return [adx, ady]
        return [0, 0]

    if res:
        best = None
        best_score = 10**9
        for x, y in res:
            d = abs(x - sx) + abs(y - sy)
            if (x, y) == (ox, oy):
                continue
            score = d
            if ox != x or oy != y:
                score += 0.2 * (abs(x - ox) + abs(y - oy))
            if score < best_score:
                best_score = score
                best = (x, y)
        if best is not None:
            return step_toward(best[0], best[1], sx, sy)

    tx = w - 1 if sx < (w - 1 - sx) else 0
    ty = h - 1 if sy < (h - 1 - sy) else 0
    tx = (w - 1 if sx < ox else 0) if w > 1 else 0
    ty = (h - 1 if sy < oy else 0) if h > 1 else 0

    return step_toward(tx, ty, sx, sy)