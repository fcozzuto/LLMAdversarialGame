def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inside(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = [(dx, dy) for dx, dy in moves if legal(dx, dy)]
    if not cands:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            d_before = abs(sx - ox) + abs(sy - oy)
            d_after = abs(nx - ox) + abs(ny - oy)
            v = (d_before - d_after) * 10 - (abs(nx - w // 2) + abs(ny - h // 2))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    resources = [tuple(r) for r in resources if len(r) >= 2]
    best = None
    bestv = -10**18

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy

        best_self_d = 10**9
        best_target = None
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best_self_d or (d == best_self_d and (rx, ry) < best_target):
                best_self_d = d
                best_target = (rx, ry)

        rx, ry = best_target
        self_d = abs(nx - rx) + abs(ny - ry)
        opp_d = abs(ox - rx) + abs(oy - ry)
        score = (opp_d - self_d) * 20 - self_d + (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))

        if score > bestv or (score == bestv and (dx, dy) < best):
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]