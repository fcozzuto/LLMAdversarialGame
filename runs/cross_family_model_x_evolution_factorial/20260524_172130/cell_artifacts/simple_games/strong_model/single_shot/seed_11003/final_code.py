def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return [int(v[0]), int(v[1])]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("X", "Y"), (0, 1)):
                if a in v and b in v:
                    return [int(v[a]), int(v[b])]
        return None

    def pt(p, q):
        return abs(p[0] - q[0]) + abs(p[1] - q[1])

    p = xy(observation.get("self_position")) or [0, 0]
    o = xy(observation.get("opponent_position"))
    res = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    score = observation.get("scores") or [0, 0]
    if isinstance(score, dict):
        a, b = score.get("self", 0), score.get("opponent", 0)
    else:
        a = score[0] if len(score) > 0 else 0
        b = score[1] if len(score) > 1 else 0

    blocks = set()
    for z in obs:
        q = xy(z)
        if q is not None:
            blocks.add((q[0], q[1]))

    target = None
    best = None
    for r in res:
        q = xy(r)
        if q is None:
            continue
        d = pt(p, q)
        if best is None or d < best or (d == best and (q[0], q[1]) < (target[0], target[1])):
            best = d
            target = q

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if target is not None:
        if o is not None and a < b:
            target = o
        elif o is not None and a == b and best is not None and pt(p, o) + 1 < best:
            target = o
        dx = 0 if target[0] == p[0] else (1 if target[0] > p[0] else -1)
        dy = 0 if target[1] == p[1] else (1 if target[1] > p[1] else -1)
        pref = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
    else:
        pref = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]

    for dx, dy in pref + moves:
        np = (p[0] + dx, p[1] + dy)
        if np not in blocks:
            return [dx, dy]
    return [0, 0]
