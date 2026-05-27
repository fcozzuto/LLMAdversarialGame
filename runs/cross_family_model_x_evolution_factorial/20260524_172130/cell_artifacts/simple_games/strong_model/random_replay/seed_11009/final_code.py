def choose_move(observation):
    def num(v):
        try:
            return int(v)
        except Exception:
            return 0

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return [num(v[0]), num(v[1])]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("row", "col"), ("r", "c")):
                if a in v and b in v:
                    return [num(v[a]), num(v[b])]
        return None

    def get(*keys):
        if isinstance(observation, dict):
            for k in keys:
                if k in observation:
                    return observation[k]
        return None

    me = pos(get("self_position", "position", "my_position", "agent_position", "self")) or [0, 0]
    op = pos(get("opponent_position", "enemy_position", "other_position", "opponent", "enemy")) or [0, 0]
    w = num(get("grid_width", "width"))
    h = num(get("grid_height", "height"))
    if w <= 0: w = 1
    if h <= 0: h = 1

    res = []
    r = get("resources")
    if isinstance(r, dict):
        for v in r.values():
            p = pos(v)
            if p: res.append(p)
    elif isinstance(r, (list, tuple, set)):
        for v in r:
            p = pos(v)
            if p: res.append(p)

    obs = set()
    o = get("obstacles")
    if isinstance(o, dict):
        for v in o.values():
            p = pos(v)
            if p: obs.add((p[0], p[1])) if p else None
    elif isinstance(o, (list, tuple, set)):
        for v in o:
            p = pos(v)
            if p: obs.add((p[0], p[1]))

    best = None
    bestd = 10**9
    for p in res:
        d = abs(p[0] - me[0]) + abs(p[1] - me[1])
        if d < bestd:
            bestd = d
            best = p
    if best is None:
        best = op if num(get("scores", {}).get("self", 0) if isinstance(get("scores"), dict) else 0) <= num(get("scores", {}).get("opponent", 0) if isinstance(get("scores"), dict) else 0) else [w // 2, h // 2]

    bx = 0 if best[0] == me[0] else (1 if best[0] > me[0] else -1)
    by = 0 if best[1] == me[1] else (1 if best[1] > me[1] else -1)
    moves = [(bx, by), (bx, 0), (0, by), (bx, -by), (-bx, by), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]

    seen = set()
    for dx, dy in moves:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        x, y = me[0] + dx, me[1] + dy
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            return [dx, dy]
    return [0, 0]
