def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", None)
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return None

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = xy(observation.get("self_position", [0, 0])) or (0, 0)
    ox, oy = xy(observation.get("opponent_position", [0, 0])) or (0, 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        q = xy(p)
        if q is not None:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        q = xy(r)
        if q is not None:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b, c, d):
        t = a - c
        if t < 0: t = -t
        u = b - d
        if u < 0: u = -u
        return t + u

    tx, ty = min(res, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    cands = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**9), 0, 0)
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        score = -md(nx, ny, tx, ty)
        score = score * 2 - md(nx, ny, ox, oy)
        t = (score, dx, dy)
        if t > best:
            best = t
    return [best[1], best[2]]