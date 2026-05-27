def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}
    w = int(g.get("grid_width", 0) or 0)
    h = int(g.get("grid_height", 0) or 0)

    def pos(v, d=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try: return int(v[0]), int(v[1])
            except: return d
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                try: return int(v["x"]), int(v["y"])
                except: return d
        return d

    def lst(v):
        return v if isinstance(v, (list, tuple)) else []

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    s = pos(g.get("self_position"))
    o = pos(g.get("opponent_position"))
    res = [pos(x) for x in lst(g.get("resources"))]
    obs = {pos(x) for x in lst(g.get("obstacles"))}
    sp = {pos(x) for x in lst(g.get("self_path"))}
    op = {pos(x) for x in lst(g.get("opponent_path"))}
    avoid = obs | sp | op

    def valid(p):
        return 0 <= p[0] < w and 0 <= p[1] < h and p not in obs

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            p = (s[0] + dx, s[1] + dy)
            if valid(p):
                score = 0
                if res:
                    score -= min(dist(p, r) for r in res) * 10
                score -= dist(p, o) * 2
                if p in avoid:
                    score -= 50
                score -= abs(dx) + abs(dy)
                cand.append((score, dx, dy))
    if cand:
        cand.sort(key=lambda t: (-t[0], abs(t[1]) + abs(t[2]), t[1], t[2]))
        return [cand[0][1], cand[0][2]]

    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        p = (s[0] + dx, s[1] + dy)
        if valid(p):
            return [dx, dy]
    return [0, 0]
