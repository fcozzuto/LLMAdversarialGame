def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    best = (0, 0)
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            v = -10**12
        else:
            if res:
                md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
                v = -md
            else:
                v = -(abs(nx - ox) + abs(ny - oy))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]