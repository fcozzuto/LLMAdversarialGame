def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}
    def pt(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try: return int(v[0]), int(v[1])
            except: return None
        if isinstance(v, dict):
            try:
                if "x" in v and "y" in v: return int(v["x"]), int(v["y"])
            except: pass
        return None
    def pts(v):
        r = []
        if isinstance(v, dict):
            for x in v.values():
                q = pt(x)
                if q is not None: r.append(q)
        elif isinstance(v, (list, tuple, set)):
            for x in v:
                q = pt(x)
                if q is not None: r.append(q)
        else:
            q = pt(v)
            if q is not None: r.append(q)
        return r
    w = int(g.get("grid_width", 0) or 0); h = int(g.get("grid_height", 0) or 0)
    s = pt(g.get("self_position")) or pt(g.get("position")) or (0, 0)
    o = pt(g.get("opponent_position")) or (0, 0)
    blocked = set(pts(g.get("obstacles")))
    for k in ("self_path", "opponent_path", "path", "trail", "visited", "walls", "blocked", "hazards"):
        blocked.update(pts(g.get(k)))
    resources = []
    for k in ("resources", "resource_positions", "resource_positions_list", "food"):
        resources += pts(g.get(k))
    cand = [(0,1),(1,0),(0,-1),(-1,0),(0,0)]
    best = (0, 0)
    bestv = -10**9
    for dx, dy in cand:
        nx, ny = s[0] + dx, s[1] + dy
        if w and (nx < 0 or nx >= w): continue
        if h and (ny < 0 or ny >= h): continue
        if (nx, ny) in blocked: continue
        v = 0
        if resources:
            d = min(abs(nx - x) + abs(ny - y) for x, y in resources)
            v -= d * 10
            if (nx, ny) in resources: v += 1000
        else:
            v -= abs(nx - o[0]) + abs(ny - o[1])
        if dx == 0 and dy == 0: v -= 2
        if abs(nx - o[0]) + abs(ny - o[1]) == 1: v += 3
        if v > bestv: bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]
