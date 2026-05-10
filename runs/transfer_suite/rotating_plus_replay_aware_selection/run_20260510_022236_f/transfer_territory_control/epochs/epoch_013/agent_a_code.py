def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1)) or (w - 1, h - 1)
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    target = None
    if res:
        target = min(res, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        target = (ox, oy)

    def score(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        d1 = abs(nx - target[0]) + abs(ny - target[1])
        d2 = abs(nx - ox) + abs(ny - oy)
        myc = int(observation.get("self_territory_count") or 0)
        opc = int(observation.get("opponent_territory_count") or 0)
        if myc <= opc:
            return -d1 + 0.2 * d2
        return -d1 + 0.6 * d2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            sc = score(nx, ny)
            if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]