def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources_raw = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh.sort()

    def m(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = (0, 0)
    bestv = -10**18

    if res:
        scored = []
        for rx, ry in res:
            ds = m(sx, sy, rx, ry)
            do = m(ox, oy, rx, ry)
            scored.append((ds - do, ds, rx, ry))
        scored.sort()
        _, _, tx, ty = scored[0]
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            ds = m(nx, ny, tx, ty)
            do = m(ox, oy, tx, ty)
            v = -ds + (1 if ds <= do else 0) - 0.01 * (m(nx, ny, ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: drift to the corner farthest from opponent, avoiding obstacles.
    tx = 0 if ox > (w - 1) // 2 else w - 1
    ty = 0 if oy > (h - 1) // 2 else h - 1
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = m(nx, ny, tx, ty) - 0.01 * m(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]