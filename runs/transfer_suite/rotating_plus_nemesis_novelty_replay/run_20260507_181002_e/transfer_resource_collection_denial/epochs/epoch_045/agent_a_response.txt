def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", v.get("location", None)))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", (0, 0)))
    ox, oy = get_xy(observation.get("opponent_position", (sx, sy)))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))
    if not resources:
        deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        # drift away from opponent slightly
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            ad = abs(nx - ox) + abs(ny - oy)
            if best is None or ad > best[0]:
                best = (ad, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick the resource with best advantage: (opp_dist - self_dist), then closer self_dist
    best_t = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd)
        if best_t is None or key > best_t[0]:
            best_t = (key, tx, ty)
    _, tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: stay away from opponent
        cand = (sd2, -od2, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[2], best[3]] if best else [0, 0]