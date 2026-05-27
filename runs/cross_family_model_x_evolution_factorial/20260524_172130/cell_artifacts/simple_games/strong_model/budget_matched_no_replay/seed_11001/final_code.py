def choose_move(observation):
    def g(k, d=None):
        try:
            return observation.get(k, d)
        except Exception:
            return d

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return [int(v[0]), int(v[1])]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("row", "col"), ("r", "c")):
                if a in v and b in v:
                    return [int(v[a]), int(v[b])]
        return None

    s = pos(g("self_position")) or [0, 0]
    o = pos(g("opponent_position")) or [0, 0]
    res = g("resources") or []
    obs = g("obstacles") or []
    w = int(g("grid_width", 0) or 0)
    h = int(g("grid_height", 0) or 0)

    rs = []
    for r in res:
        p = pos(r)
        if p is not None:
            rs.append(p)

    def bad(x, y):
        if w and (x < 0 or x >= w): return True
        if h and (y < 0 or y >= h): return True
        for p in obs:
            q = pos(p)
            if q is not None and q[0] == x and q[1] == y:
                return True
        return False

    def step_toward(t):
        dx = 0 if t[0] == s[0] else (1 if t[0] > s[0] else -1)
        dy = 0 if t[1] == s[1] else (1 if t[1] > s[1] else -1)
        cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        best = [0, 0]
        for a, b in cand:
            nx, ny = s[0] + a, s[1] + b
            if not bad(nx, ny):
                if abs(nx - t[0]) + abs(ny - t[1]) < abs(s[0] - t[0]) + abs(s[1] - t[1]):
                    return [a, b]
                best = [a, b]
        return best

    if rs:
        rs.sort(key=lambda p: (abs(p[0] - s[0]) + abs(p[1] - s[1]), abs(p[0] - o[0]) + abs(p[1] - o[1]), p[1], p[0]))
        mv = step_toward(rs[0])
        if mv != [0, 0]:
            return mv

    sx = 1 if o[0] > s[0] else (-1 if o[0] < s[0] else 0)
    sy = 1 if o[1] > s[1] else (-1 if o[1] < s[1] else 0)
    for mv in ([sx, sy], [sx, 0], [0, sy], [sx, -sy], [-sx, sy], [1, 0], [0, 1], [-1, 0], [0, -1], [0, 0]):
        nx, ny = s[0] + mv[0], s[1] + mv[1]
        if not bad(nx, ny):
            return [mv[0], mv[1]]
    return [0, 0]
