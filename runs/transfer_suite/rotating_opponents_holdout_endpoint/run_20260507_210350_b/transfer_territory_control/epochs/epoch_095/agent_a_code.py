def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    opp = observation.get("opponent_position")
    try:
        ox, oy = (int(opp[0]), int(opp[1])) if opp is not None else (sx, sy)
    except:
        ox, oy = sx, sy

    # Choose best target: nearest unclaimed, else nearest opponent.
    target = None
    bestd = None
    for p in unclaimed:
        px, py = p
        try:
            px, py = int(px), int(py)
        except:
            continue
        d = abs(px - sx) + abs(py - sy)
        if bestd is None or d < bestd or (d == bestd and (px, py) < target):
            bestd = d
            target = (px, py)
    if target is None:
        target = (ox, oy)

    best = None
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moving closer to target, break ties deterministically, avoid moving toward opponent when unclaimed exists.
        dist_to_t = abs(nx - target[0]) + abs(ny - target[1])
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        toward_opp_pen = 0
        if unclaimed:
            toward_opp_pen = (-(dist_to_opp))  # larger dist_to_opp is better
        score = dist_to_t + toward_opp_pen
        key = (score, dist_to_opp, dx, dy)
        if bestscore is None or key < bestscore:
            bestscore = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]