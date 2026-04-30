def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    # Deterministic tie-break: fixed order above, no randomness.

    def score_move(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            d = cheb(nx, ny, int(round(cx)), int(round(cy)))
            return -d
        best = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            diff = od - sd  # positive means we can reach sooner
            take = 2000 if (nx == rx and ny == ry) else 0
            # Prefer being ahead, while still moving toward targets.
            sc = take + diff * 40 - sd * 3
            if sc > best:
                best = sc
        # Small preference to keep distance from opponent when not capturing.
        opp_d = cheb(nx, ny, ox, oy)
        return best + opp_d * 1

    best_sc = -10**18
    best_mv = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = score_move(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]