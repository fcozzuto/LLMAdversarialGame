def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    s = observation.get("self_position", (0, 0))
    o = observation.get("opponent_position", (0, 0))
    rs = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    sp = observation.get("self_path", []) or []
    op = observation.get("opponent_path", []) or []
    if not isinstance(s, (list, tuple)) or len(s) < 2:
        s = (0, 0)
    if not isinstance(o, (list, tuple)) or len(o) < 2:
        o = (w - 1, h - 1)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))
    best = None
    bd = 10**9
    if isinstance(rs, dict):
        rs = list(rs.values())
    for r in rs:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            d = abs(x - sx) + abs(y - sy)
            if d < bd:
                bd = d
                best = (x, y)
    if best is None:
        if len(sp) > len(op):
            dx = 1 if sx < w - 1 else -1 if sx > 0 else 0
            dy = 0
        else:
            dx = -1 if sx > ox else (1 if sx < ox else 0)
            dy = -1 if sy > oy else (1 if sy < oy else 0)
        if (sx + dx, sy + dy) in blocked:
            if (sx, sy + (1 if sy < h - 1 else -1 if sy > 0 else 0)) not in blocked:
                return [0, 1 if sy < h - 1 else -1 if sy > 0 else 0]
            return [1 if sx < w - 1 else -1 if sx > 0 else 0, 0]
        return [dx, dy]
    dx = 1 if best[0] > sx else -1 if best[0] < sx else 0
    dy = 1 if best[1] > sy else -1 if best[1] < sy else 0
    if abs(best[0] - sx) >= abs(best[1] - sy):
        cand = [(dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy)]
    else:
        cand = [(0, dy), (dx, 0), (dx, dy), (0, -dy), (-dx, 0)]
    for a, b in cand:
        nx, ny = sx + a, sy + b
        if -1 <= a <= 1 and -1 <= b <= 1 and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [a, b]
    return [0, 0]
