def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def edge_pen(x, y):
        return ((x == 0) or (x == w - 1)) + ((y == 0) or (y == h - 1))

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            score = -d - 0.03 * edge_pen(nx, ny)
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Rank resources by who is closer; prefer ones where we are closer.
    scored = []
    for rx, ry in resources:
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        # Higher is better: strong bias for resources we can reach first.
        val = (1 if ds < do else 0)
        tie = 1 if ds == do else 0
        # Encourage being closer even when we aren't first.
        score = (3.0 * val) + (0.4 * tie) - 0.001 * ds
        scored.append((score, rx, ry, ds, do))
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))

    # Evaluate each move by its best reachable resource advantage from the next cell.
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        best_move_score = -10**18
        for i in range(6 if len(scored) > 6 else len(scored)):
            score0, rx, ry, ds0, do0 = scored[i]
            ds1 = dist2(nx, ny, rx, ry)
            do1 = dist2(ox, oy, rx, ry)
            win = 1 if ds1 < do1 else 0
            tie = 1 if ds1 == do1 else 0
            # Combine: chosen resource advantage + improved distance.
            s = (4.0 * win) + (0.6 * tie) + score0 - 0.0015 * ds1 - 0.01 * edge_pen(nx, ny)
            if s > best_move_score:
                best_move_score = s
        if best_move_score > best[0] or (best_move_score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (best_move_score, dx, dy)
    return [best[1], best[2]]