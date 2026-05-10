def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    opp_d = abs(sx - ox) + abs(sy - oy)
    candidates = [(abs(cx - ox) + abs(cy - oy), -((abs(cx - sx) + abs(cy - sy))), cx, cy) for (cx, cy) in unclaimed if ok(cx, cy)]
    if candidates:
        _, _, tx, ty = sorted(candidates)[-1]
    else:
        tx, ty = ox, oy
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        score = (d_opp * 2 - d_to)
        if (nx, ny) in unclaimed:
            score += 5
        if dx == 0 and dy == 0:
            score -= 1 + (opp_d < 2)
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]