def choose_move(observation):
    def p(v, d=(0, 0)):
        try:
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return int(v[0]), int(v[1])
        except:
            pass
        return d

    def sgn(x):
        return -1 if x < 0 else (1 if x > 0 else 0)

    def step(a, b):
        return [sgn(b[0] - a[0]), sgn(b[1] - a[1])]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = p(observation.get("self_position"))
    opp = p(observation.get("opponent_position"), me)
    obs = set()
    for q in observation.get("obstacles") or []:
        obs.add(p(q))
    res = []
    for q in observation.get("resources") or []:
        if isinstance(q, dict):
            q = q.get("position", q.get("pos", q))
        res.append(p(q))
    if res:
        t = min(res, key=lambda r: (man(me, r), man(opp, r), r[0], r[1]))
        dx, dy = step(me, t)
        if dx or dy:
            nx, ny = me[0] + dx, me[1] + dy
            if (nx, ny) not in obs:
                return [dx, dy]
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        best = [0, 0]
        score = None
        for d in dirs:
            nx, ny = me[0] + d[0], me[1] + d[1]
            if (nx, ny) in obs:
                continue
            v = (man((nx, ny), t), man((nx, ny), opp), -d[0], -d[1])
            if score is None or v < score:
                score = v
                best = [d[0], d[1]]
        return best
    dx, dy = step(me, opp)
    if dx or dy:
        nx, ny = me[0] + dx, me[1] + dy
        if (nx, ny) not in obs:
            return [dx, dy]
    for d in [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]:
        nx, ny = me[0] + d[0], me[1] + d[1]
        if (nx, ny) not in obs:
            return [d[0], d[1]]
    return [0, 0]
