def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("row", "col"), ("i", "j")):
                if a in v and b in v:
                    return v[a], v[b]
        return None

    s = pos(observation.get("self_position")) or (0, 0)
    o = pos(observation.get("opponent_position")) or (0, 0)
    blocks = {tuple(x) for x in observation.get("obstacles", []) if isinstance(x, (list, tuple)) and len(x) >= 2}
    res = [pos(x) for x in observation.get("resources", [])]
    res = [p for p in res if p is not None]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    target = None
    best = 10**9
    for p in res:
        d = abs(p[0] - s[0]) + abs(p[1] - s[1])
        if d < best:
            best = d
            target = p
    if target is None:
        target = o

    dx = 0 if target[0] == s[0] else (1 if target[0] > s[0] else -1)
    dy = 0 if target[1] == s[1] else (1 if target[1] > s[1] else -1)

    cand = [(dx, dy), (dx, 0), (0, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    for a, b in cand:
        nx, ny = s[0] + a, s[1] + b
        if ok(nx, ny):
            return [a, b]
    return [0, 0]
