def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unC = observation.get("unclaimed_cells") or []
    targets = []
    for p in unC:
        if p and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    if not targets:
        targets = [(ox, oy)]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (10**18, 10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dmin = 10**18
        for tx, ty in targets[:30]:
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if d < dmin:
                dmin = d
        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # primary: get closer to target, secondary: avoid being too close to opponent
        cand = (dmin, -do, dx, dy)
        if cand < best:
            best = cand
    return [best[2], best[3]]