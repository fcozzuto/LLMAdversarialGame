def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources: move to maximize distance from opponent while staying valid
        best = (0, -10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny):
                    continue
                d_opp = cheb(nx, ny, ox, oy)
                # Tie-break: prefer moving toward center and lexicographic stability
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                center_bias = -(abs(nx - cx) + abs(ny - cy))
                key = (dx, d_opp + center_bias, -dx, -dy)
                if key > best:
                    best = key
        return [best[2], best[3]] if best[1] != -10**9 else [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # Choose target resource: prioritize ones closer to us than opponent, but avoid far-away targets.
    best_r = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower score is better
        center = abs(rx - cx) + abs(ry - cy)
        score = (2.5 * ds - 1.7 * do) + 0.08 * center
        # Deterministic tie-break
        key = (score, ds - do, ds, rx, ry)
        if best_score is None or key < best_score:
            best_score = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Choose one-step move minimizing distance to target; also avoid letting opponent get too close.
    best_move = (10**9, -10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d_to_t = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer being nearer to target; if tie, prefer farther from opponent; then stable tie-break
            key = (d_to_t, -(d_opp), abs(nx - tx) + abs(ny - ty), dx, dy)
            # Want lexicographically smallest key, but with distance/opponent signs handled above
            cand = (key[0], key[1], -key[2], dx, dy)
            if cand < best_move:
                best_move = cand

    return [int(best_move[3]), int(best_move[4])] if best_move[0] != 10**9 else [0, 0]