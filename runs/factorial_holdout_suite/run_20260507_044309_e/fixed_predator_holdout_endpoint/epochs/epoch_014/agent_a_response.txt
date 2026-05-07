def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        # Move toward the center of the remaining space relative to opponent.
        tx = (w - 1 + sx - ox) // 2
        ty = (h - 1 + sy - oy) // 2
        best, bestv = (0, 0, sx, sy), -10**18
        for dx, dy, nx, ny in cand:
            v = -(md(nx, ny, tx, ty)) - 0.01 * md(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy, nx, ny)
        return [best[0], best[1]]

    # Choose move that maximizes "dominance" over opponent for a small set of best local targets.
    # Dominance for a resource r: (opp_dist - self_dist). Also include closeness to our best target.
    # Additionally prefer moving away from traps near obstacles by mild penalty for being adjacent to obstacles.
    def obs_adj_pen(nx, ny):
        p = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = nx + ax, ny + ay
            if (x, y) in obstacles:
                p += 1
        return p

    # Pre-rank resources by our current distance, keep top K for speed and determinism.
    res_sorted = sorted(resources, key=lambda r: md(sx, sy, r[0], r[1]))
    K = 6 if len(res_sorted) >= 6 else len(res_sorted)
    targets = res_sorted[:K]

    bestdx, bestdy, bestv = 0, 0, -10**18
    for dx, dy, nx, ny in cand:
        # Best target after this move
        our_dists = [md(nx, ny, r[0], r[1]) for r in targets]
        opp_dists = [md(ox, oy, r[0], r[1]) for r in targets]
        # Dominance objective: maximize minimum dominance among top targets, plus bias to nearest target.
        doms = [(opp_dists[i] - our_dists[i]) for i in range(len(targets))]
        min_dom = min(doms) if doms else -10**6
        best_dom = max(doms) if doms else -10**6
        best_self = min(our_dists) if our_dists else 10**6
        v = 3.0 * min_dom + 0.8 * best_dom - 0.05 * best_self - 0.02 * obs_adj_pen(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < (bestdx, bestdy)):
            bestv, bestdx, bestdy = v, dx, dy
    return [bestdx, bestdy]