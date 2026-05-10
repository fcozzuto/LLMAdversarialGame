def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    gw, gh = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    yield dx, dy, nx, ny

    if not resources:
        cx, cy = gw // 2, gh // 2
        best_move = [0, 0]
        best_val = abs(cx - sx) + abs(cy - sy)
        for dx, dy, nx, ny in neighbors(sx, sy):
            v = abs(cx - nx) + abs(cy - ny)
            if v < best_val:
                best_val, best_move = v, [dx, dy]
        return best_move

    # Choose target resource with strongest lead over opponent.
    best = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        # Primary: opponent behind us; Secondary: closer to us; Tertiary: deterministic tie on position.
        lead = opd - myd
        if best is None or (lead, -myd, -(rx + ry)) > (best[0], best[1], best[2]):
            best = (lead, -myd, -(rx + ry), rx, ry)

    _, _, _, tx, ty = best

    # Greedy step that reduces distance to target, while blocking obstacle hits.
    curd = abs(tx - sx) + abs(ty - sy)
    best_move = [0, 0]
    best_val = curd
    for dx, dy, nx, ny in neighbors(sx, sy):
        v = abs(tx - nx) + abs(ty - ny)
        # Small deterministic preference to move generally toward target when equal distance.
        if v < best_val or (v == best_val and (dx != 0 or dy != 0) and ((nx - sx) * (tx - sx) + (ny - sy) * (ty - sy) > 0)):
            best_val = v
            best_move = [dx, dy]
    return best_move