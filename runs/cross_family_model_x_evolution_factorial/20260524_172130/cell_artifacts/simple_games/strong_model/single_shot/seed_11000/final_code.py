def choose_move(observation):
    def sign(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def pt(v):
        if isinstance(v, dict):
            for k in ("position", "pos", "location", "loc", "xy", "coord", "coords", "tile"):
                p = pt(v.get(k))
                if p is not None:
                    return p
            x = v.get("x")
            y = v.get("y")
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                return [x, y]
        elif isinstance(v, (list, tuple)):
            if len(v) >= 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                return [v[0], v[1]]
            for a in v:
                p = pt(a)
                if p is not None:
                    return p
        return None

    def points(v):
        out = []
        if v is None:
            return out
        if isinstance(v, dict):
            p = pt(v)
            if p is not None:
                out.append(p)
            else:
                for a in v.values():
                    out.extend(points(a))
        elif isinstance(v, (list, tuple)):
            if len(v) >= 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                out.append([v[0], v[1]])
            else:
                for a in v:
                    out.extend(points(a))
        return out

    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    s = pt(observation.get("self_position")) or [0, 0]
    o = pt(observation.get("opponent_position")) or [w - 1, h - 1]
    res = points(observation.get("resources"))
    obs = {tuple(p) for p in points(observation.get("obstacles"))}

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def step_toward(t):
        dx = sign(t[0] - s[0])
        dy = sign(t[1] - s[1])
        cand = [(dx, 0), (0, dy), (dx, dy), (dx, -dy), (-dx, dy)]
        for mx, my in cand:
            if mx or my:
                nx, ny = s[0] + mx, s[1] + my
                if free(nx, ny):
                    return [mx, my]
        for mx, my in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if free(s[0] + mx, s[1] + my):
                return [mx, my]
        return [0, 0]

    best = None
    if res:
        for r in res:
            d = abs(r[0] - s[0]) + abs(r[1] - s[1])
            if best is None or d < best[0]:
                best = (d, r)
    if best is not None:
        mv = step_toward(best[1])
        if mv != [0, 0]:
            return mv

    if w and h:
        goal = [0, 0] if (s[0] + s[1]) % 2 == 0 else [w - 1, h - 1]
        mv = step_toward(goal)
        if mv != [0, 0]:
            return mv

    for mx, my in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        if free(s[0] + mx, s[1] + my):
            return [mx, my]
    return [0, 0]
