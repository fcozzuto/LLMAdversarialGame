def choose_move(observation):
    def p(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return [int(v[0]), int(v[1])]
        return None

    def pts(v):
        out = []
        if isinstance(v, dict):
            for x in v.values():
                q = p(x)
                if q is not None: out.append(q)
                elif isinstance(x, (list, tuple)):
                    for y in x:
                        q = p(y)
                        if q is not None: out.append(q)
        elif isinstance(v, (list, tuple)):
            for x in v:
                q = p(x)
                if q is not None: out.append(q)
                elif isinstance(x, dict):
                    for y in x.values():
                        q = p(y)
                        if q is not None: out.append(q)
        return out

    def md(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def sgn(x): return 0 if x == 0 else (1 if x > 0 else -1)

    s = p(observation.get("self_position")) or [0, 0]
    o = p(observation.get("opponent_position")) or [0, 0]
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    obs = {tuple(x) for x in pts(observation.get("obstacles"))}
    res = pts(observation.get("resources"))
    cur = md(s, o)
    best = [0, 0]
    bestv = -10**9

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = s[0] + dx, s[1] + dy
            if w and (nx < 0 or nx >= w): continue
            if h and (ny < 0 or ny >= h): continue
            if (nx, ny) in obs: continue
            v = 0
            if res:
                d = min(md([nx, ny], r) for r in res)
                v -= d * 4
                v += max(0, cur - md([nx, ny], o)) * 2
            else:
                v += max(0, cur - md([nx, ny], o)) * 3
                v -= abs(dx) + abs(dy)
            if dx == 0 and dy == 0: v -= 1
            if v > bestv or (v == bestv and [dx, dy] < best):
                bestv, best = v, [dx, dy]
    return best
