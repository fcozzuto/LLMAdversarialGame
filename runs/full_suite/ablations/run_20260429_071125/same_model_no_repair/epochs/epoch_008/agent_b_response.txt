def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Deterministic: drift toward center while keeping away from obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**18)  # (dx,dy,score)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            score -= 0.1 * dist(nx, ny, ox, oy)
            if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Choose target resource by distance advantage vs opponent.
    best_target = None
    best_key = None  # sort key: larger advantage, then smaller self distance, then position
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, -((rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Greedy one-step move minimizing our distance to target, avoiding obstacles and boundaries.
    best = (0, 0, 10**18, -10**18)  # (dx,dy,ourdist,blockscore)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        nd = dist(nx, ny, tx, ty)
        # Secondary: discourage walking into immediate opponent threat to same target.
        nod = dist(ox, oy, tx, ty)
        threat = (nod - nd)
        blockscore = threat
        # tie-break: prefer moves that also increase advantage vs opponent by approaching the target
        if nd < best[2] or (nd == best[2] and (blockscore > best[3] or (blockscore == best[3] and (dx, dy) < (best[0], best[1])))):
            best = (dx, dy, nd, blockscore)

    return [best[0], best[1]]