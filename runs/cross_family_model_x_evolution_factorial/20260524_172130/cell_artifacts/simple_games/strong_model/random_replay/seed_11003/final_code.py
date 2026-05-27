def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return [int(v[0]), int(v[1])]
        if isinstance(v, dict):
            for a, b in (("x", "y"), ("row", "col"), ("r", "c")):
                if a in v and b in v:
                    return [int(v[a]), int(v[b])]
            for k in ("position", "pos", "loc", "location", "cell", "target"):
                if k in v:
                    p = pos(v[k])
                    if p is not None:
                        return p
        return None

    me = pos(g.get("self_position")) or [0, 0]
    op = pos(g.get("opponent_position"))
    w = int(g.get("grid_width", g.get("width", 0)) or 0)
    h = int(g.get("grid_height", g.get("height", 0)) or 0)

    resources = g.get("resources") or []
    obstacles = g.get("obstacles") or []
    banned = set()
    for t in obstacles:
        p = pos(t)
        if p is not None:
            banned.add((p[0], p[1]))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_d = 10**9
    if resources:
        for r in resources:
            p = pos(r)
            if p is not None and (p[0], p[1]) not in banned:
                d = dist(me, p)
                if d < best_d:
                    best_d = d
                    best = p

    if best is None:
        if op is not None:
            dx = 1 if me[0] < op[0] else -1 if me[0] > op[0] else 0
            dy = 1 if me[1] < op[1] else -1 if me[1] > op[1] else 0
        else:
            dx, dy = 1, 0
    else:
        dx = 1 if me[0] < best[0] else -1 if me[0] > best[0] else 0
        dy = 1 if me[1] < best[1] else -1 if me[1] > best[1] else 0
        if op is not None and dist(me, op) <= 2 and dist([me[0] + dx, me[1] + dy], op) < dist(me, op):
            if abs(me[0] - op[0]) >= abs(me[1] - op[1]):
                dx = -dx if dx else (1 if me[0] <= op[0] else -1)
            else:
                dy = -dy if dy else (1 if me[1] <= op[1] else -1)

    nx, ny = me[0] + dx, me[1] + dy
    if (nx, ny) in banned or (w and not (0 <= nx < w)) or (h and not (0 <= ny < h)):
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            nx, ny = me[0] + a, me[1] + b
            if (nx, ny) not in banned and (not w or 0 <= nx < w) and (not h or 0 <= ny < h):
                return [a, b]
        return [0, 0]
    return [dx, dy]
