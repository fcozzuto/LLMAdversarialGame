def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    opp = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = (int(opp[0]), int(opp[1])) if isinstance(opp, (list, tuple)) and len(opp) == 2 else (w - 1, h - 1)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                x, y = int(p[0]), int(p[1])
                obs.add((x, y))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inside(x, y) and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                res.append((int(p[0]), int(p[1])))
            except:
                pass
    unclaimed = observation.get("unclaimed_cells") or []
    uc = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                uc.append((int(p[0]), int(p[1])))
            except:
                pass

    target = None
    if res:
        target = min(res, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy) + (0.001 * t[0] + 0.0001 * t[1]))
    elif uc:
        target = min(uc, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy) + (0.001 * t[0] + 0.0001 * t[1]))
    else:
        target = (ox, oy)

    moves = [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1)]
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist_t = abs(nx - target[0]) + abs(ny - target[1])
        dist_o = abs(nx - ox) + abs(ny - oy)
        # Prefer reducing distance to target, and (slightly) moving away from opponent
        val = -dist_t * 10 + dist_o * 1
        # Deterministic tie-breaker by move order
        if val > best[2]:
            best = (dx, dy, val)
    return [best[0], best[1]]