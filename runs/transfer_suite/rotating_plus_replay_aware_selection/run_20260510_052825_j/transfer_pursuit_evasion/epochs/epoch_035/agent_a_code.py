def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    if observation.get("self_role"):
        sr = str(observation.get("self_role")).lower()
        prefer_avoid = ("evad" in sr) or ("avoid" in sr)
    else:
        prefer_avoid = False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d = bx - ax
        e = by - ay
        return d * d + e * e

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if res:
            score += -min(dist((nx, ny), t) for t in res)
        else:
            score += -dist((nx, ny), (ox, oy)) if not prefer_avoid else dist((nx, ny), (ox, oy))
        candidates.append((score, dx, dy))

    if not candidates:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    candidates.sort(key=lambda z: (-z[0], deltas.index((z[1], z[2]))))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]