def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set((r[0], r[1]) for r in resources)
    if not res_set:
        # fallback: move toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, abs(nx - sx) + abs(ny - sy), dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose the move that maximizes (opp_dist - self_dist) to the best available resource.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        best_score = -10**9
        best_self_dist = 10**9
        for rx, ry in res_set:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            score = opp_d - self_d
            if score > best_score or (score == best_score and self_d < best_self_dist):
                best_score = score
                best_self_dist = self_d

        # Tie-break deterministically: prefer smaller self_dist, then lexicographic dx/dy by delta order.
        cand = (-(best_score), best_self_dist, deltas.index((dx, dy)))
        if best is None or cand < best:
            best = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]