def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    targets = observation.get("unclaimed_cells") or []
    if targets:
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    base = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 5000
        elif (nx, ny) in unclaimed:
            score += 180
        elif (nx, ny) in self_t:
            score += 60

        dopp = abs(nx - ox) + abs(ny - oy)
        score += (base - dopp) * 3

        to_target = abs(nx - tx) + abs(ny - ty)
        score += (abs(sx - tx) + abs(sy - ty) - to_target) * 2

        if (nx, ny) == (tx, ty):
            score += 500

        if ddx == 0 and ddy == 0:
            score -= 5

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]