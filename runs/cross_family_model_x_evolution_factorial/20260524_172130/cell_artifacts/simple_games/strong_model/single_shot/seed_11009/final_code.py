def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    w = o.get("grid_width", 0) or 0
    h = o.get("grid_height", 0) or 0

    def pos(v):
        if isinstance(v, dict):
            if isinstance(v.get("x"), (int, float)) and isinstance(v.get("y"), (int, float)):
                return [int(v["x"]), int(v["y"])]
            for k in ("pos", "position", "loc", "location"):
                p = pos(v.get(k))
                if p is not None:
                    return p
        if isinstance(v, (list, tuple)) and len(v) >= 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
            return [int(v[0]), int(v[1])]
        return None

    s = pos(o.get("self_position")) or [0, 0]
    p = pos(o.get("opponent_position"))
    rs = o.get("resources") or []
    os = o.get("obstacles") or []

    R = []
    for x in rs:
        q = pos(x)
        if q is not None:
            R.append(q)
    O = set()
    for x in os:
        q = pos(x)
        if q is not None:
            O.add((q[0], q[1]))

    best = [0, 0]
    bestv = -10**9
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = s[0] + dx, s[1] + dy
        v = 0
        if w and (nx < 0 or nx >= w) or h and (ny < 0 or ny >= h):
            v -= 1000
        if (nx, ny) in O:
            v -= 1000
        if R:
            d = min(abs(nx - a) + abs(ny - b) for a, b in R)
            v -= d * 10
        if p is not None:
            v += (abs(s[0] - p[0]) + abs(s[1] - p[1]) - abs(nx - p[0]) - abs(ny - p[1]))
        if dx == 0 and dy == 0:
            v -= 1
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best
