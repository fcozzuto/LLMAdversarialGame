def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Deterministic fallback: head toward center while staying away from opponent
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) + 0.5 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Policy: after move, prioritize reaching an unclaimed resource that is relatively less "contested"
    # by opponent. Also keep distance from opponent to avoid collision/contest.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # nearest resource distance after move
        best_r = None
        best_rd = 10**18
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best_rd or (d == best_rd and (rx, ry) < best_r):
                best_rd = d
                best_r = (rx, ry)
        rx, ry = best_r
        # contest factor: opponent distance to same resource
        dop = cheb(ox, oy, rx, ry)
        # forward push away from opponent slightly
        opp_away = cheb(nx, ny, ox, oy)
        # small tie-break toward lower resource coords deterministically
        tie = - (rx + 31 * ry)
        val = (-best_rd) + 0.35 * dop + 0.15 * opp_away + 1e-6 * tie
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]