def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p is not None and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    res = observation.get("resources") or []
    for p in res:
        if p is not None and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))

    if not targets:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        target = (cx, cy)
        use_targets = False
    else:
        best = targets[0]
        bd = abs(best[0] - x) + abs(best[1] - y)
        for tx, ty in targets[1:]:
            d = abs(tx - x) + abs(ty - y)
            if d < bd:
                bd = d
                best = (tx, ty)
        target = best
        use_targets = True

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        md_opp = abs(nx - ox) + abs(ny - oy)
        if use_targets:
            md_t = abs(nx - target[0]) + abs(ny - target[1])
            val = (200 - md_t) + (2 * md_opp)
        else:
            md_c = abs(nx - target[0]) + abs(ny - target[1])
            val = (100 - md_c) + (2 * md_opp)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    dx, dy = best_move
    return [dx, dy]