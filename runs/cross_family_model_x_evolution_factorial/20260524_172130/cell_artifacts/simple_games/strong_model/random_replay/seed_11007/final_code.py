def choose_move(observation):
    o = observation if isinstance(observation, dict) else {}
    g = lambda v, d=0: int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.lstrip("-").isdigit()) else d
    p = lambda v: [g(v[0]), g(v[1])] if isinstance(v, (list, tuple)) and len(v) > 1 else ([g(v.get("x")), g(v.get("y"))] if isinstance(v, dict) and "x" in v and "y" in v else None)
    s = p(o.get("self_position")) or [0, 0]
    e = p(o.get("opponent_position")) or [0, 0]
    w, h = g(o.get("grid_width"), 0), g(o.get("grid_height"), 0)
    if w <= 0: w = 50
    if h <= 0: h = 50
    obs = set()
    for x in o.get("obstacles", []) if isinstance(o.get("obstacles", []), (list, tuple, set)) else []:
        q = p(x)
        if q: obs.add((q[0], q[1]))
    res = []
    for x in o.get("resources", []) if isinstance(o.get("resources", []), (list, tuple, set)) else []:
        q = p(x)
        if q: res.append(q)
    if not res:
        dx = 1 if s[0] < e[0] else (-1 if s[0] > e[0] else 0)
        dy = 1 if s[1] < e[1] else (-1 if s[1] > e[1] else 0)
        if (s[0] + dx, s[1] + dy) in obs:
            for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if (s[0] + a, s[1] + b) not in obs:
                    return [a, b]
        return [dx, dy]
    path = o.get("self_path", [])
    last = p(path[-1]) if isinstance(path, (list, tuple)) and path else None
    best = None
    bestd = 10**9
    for r in res:
        d = abs(r[0] - s[0]) + abs(r[1] - s[1])
        if d < bestd or (d == bestd and (r[0], r[1]) < (best[0], best[1]) if best else True):
            best, bestd = r, d
    cand = [(best[0] - s[0], 0), (0, best[1] - s[1]), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if abs(best[0] - s[0]) < abs(best[1] - s[1]):
        cand = [(0, best[1] - s[1]), (best[0] - s[0], 0)] + cand[2:]
    score = None
    for dx, dy in cand:
        if dx > 1: dx = 1
        if dx < -1: dx = -1
        if dy > 1: dy = 1
        if dy < -1: dy = -1
        if dx == 0 and dy == 0:
            continue
        nx, ny = s[0] + dx, s[1] + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
            continue
        sc = abs(best[0] - nx) + abs(best[1] - ny)
        sc += 2 if last and [nx, ny] == last else 0
        sc += 1 if (nx, ny) == (e[0], e[1]) else 0
        if score is None or sc < score[0]:
            score = [sc, dx, dy]
    if score:
        return [score[1], score[2]]
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = s[0] + dx, s[1] + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]
