def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((nx, ny))

    if not candidates:
        return [0, 0]

    # Pick a target resource that we can reach earlier than opponent (or otherwise "least contested").
    best_t = None
    best_rank = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being earlier; otherwise prefer resources far from opponent.
        rank = (ds - do, ds, do, (rx + ry) % 2)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_t = (rx, ry)

    if best_t is None:
        # No resources visible: move to maximize distance from opponent while drifting toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_s = -10**18
        for nx, ny in candidates:
            val = cheb(nx, ny, ox, oy) - 0.05 * (abs(nx - cx) + abs(ny - cy))
            if val > best_s:
                best_s = val
                best = (nx, ny)
        bx, by = best
        return [bx - sx, by - sy]

    rx, ry = best_t
    best = None
    best_score = -10**18
    for nx, ny in candidates:
        if (nx, ny) == (rx, ry):
            score = 10**6
        else:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Encourage taking the lead; if trailing, keep away from opponent and reduce ds.
            lead = do - ds  # positive if we are closer than opponent
            dist_to_opp = cheb(nx, ny, ox, oy)
            score = 500 * lead + 2.0 * dist_to_opp - 0.2 * ds
            # Slight bias toward moving on alternating parity to avoid oscillations.
            score += 0.01 * (((nx + ny) ^ (sx + sy)) & 1)
        if score > best_score:
            best_score = score
            best = (nx, ny)

    bx, by = best
    return [bx - sx, by - sy]