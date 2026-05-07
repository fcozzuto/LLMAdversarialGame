def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in cand:
            v = -(dist(nx, ny, tx, ty)) - 0.1 * dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best_r = None
    best_v = -10**18
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise block by relative advantage.
        if sd <= od:
            v = 1000 - sd + (od - sd) * 5
        else:
            v = (od - sd) * 2 - sd
        # Mildly bias toward closer resources to ensure collection.
        v -= 0.01 * (sd + od)
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    rx, ry = best_r
    # Evaluate immediate move: prefer decreasing distance to chosen target,
    # and avoid moves that give opponent closer access to the same target.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in cand:
        sd0 = dist(sx, sy, rx, ry)
        sd1 = dist(nx, ny, rx, ry)
        # Opponent "pressure" proxy: if we move away, opponent likely wins.
        od = dist(ox, oy, rx, ry)
        opp_v = od - sd1
        v = (sd0 - sd1) * 50 + opp_v * 5 - 0.01 * dist(nx, ny, rx, ry)
        # If target already adjacent or on it, keep moving toward it.
        if sd1 == 0:
            v += 10000
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]