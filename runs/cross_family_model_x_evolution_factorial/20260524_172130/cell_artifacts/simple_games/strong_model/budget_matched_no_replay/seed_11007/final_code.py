def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("col", "row"), ("c", "r")):
                if a in v and b in v:
                    return int(v[a]), int(v[b])
        return None

    def items(v):
        out = []
        if isinstance(v, dict):
            v = v.values()
        if isinstance(v, (list, tuple)):
            for x in v:
                p = pos(x)
                if p is not None:
                    out.append(p)
        return out

    me = pos(observation.get("self_position")) or pos(observation.get("position")) or (0, 0)
    op = pos(observation.get("opponent_position")) or me
    res = items(observation.get("resources"))
    obs = set(items(observation.get("obstacles")))

    def step_toward(a, b):
        dx = 0 if a[0] == b[0] else (1 if b[0] > a[0] else -1)
        dy = 0 if a[1] == b[1] else (1 if b[1] > a[1] else -1)
        return dx, dy

    def ok(p):
        x, y = p
        return 0 <= x < w and 0 <= y < h and p not in obs

    cand = []
    for t in res:
        dx, dy = step_toward(me, t)
        cand.append((abs(t[0] - me[0]) + abs(t[1] - me[1]), dx, dy, t))
    cand.sort()

    if cand:
        _, dx, dy, t = cand[0]
        for mv in [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            if ok((me[0] + mv[0], me[1] + mv[1])):
                return [mv[0], mv[1]]

    dx, dy = step_toward(me, op)
    for mv in [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
        if ok((me[0] + mv[0], me[1] + mv[1])):
            return [mv[0], mv[1]]
    return [0, 0]
