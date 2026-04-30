def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = [0, 0]
        bestv = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    v = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                    if bestv is None or v < bestv or (v == bestv and (dx, dy) < tuple(best)):
                        bestv = v
                        best = [dx, dy]
        return best

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick resource that we can reach relatively sooner than opponent.
    target = None
    best_score = None
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        score = ds - 0.65 * do
        if best_score is None or score < best_score or (score == best_score and (ds < d2(sx, sy, target[0], target[1]) if target else True)):
            best_score = score
            target = (rx, ry)

    rx, ry = target
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                # Slightly prefer moves that don't hand opponent an immediate advantage.
                opp_next_d = d2(ox, oy, rx, ry)
                my_next_d = d2(nx, ny, rx, ry)
                step = (my_next_d - 0.2 * opp_next_d, my_next_d, abs(nx - ox) + abs(ny - oy), dx, dy)
                cand.append((step, [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: t[0])
    return cand[0][1]