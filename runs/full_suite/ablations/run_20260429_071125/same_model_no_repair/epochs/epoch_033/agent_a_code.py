def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestm, bestv = (0, 0), -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    best_over_move = None
    best_over_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Find best target for this move: prioritize where we gain distance advantage.
        best_for_move = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Encourage being closer than opponent; also prefer absolute closeness.
            v = (opd - myd) * 10 + (-myd)
            # Slightly prefer targets that are farther from opponent (harder for them).
            v += -cheb(ox, oy, rx, ry) * 0.1
            # Reduce ties deterministically by preferring lower coords.
            v += -(rx * 0.000001 + ry * 0.000002)
            if v > best_for_move:
                best_for_move = v

        # Additional: avoid moving next to opponent if it doesn't improve target advantage.
        opp_adj = cheb(nx, ny, ox, oy)
        vfinal = best_for_move - (2.0 if opp_adj <= 1 and best_for_move < 0 else 0.0)

        if vfinal > best_over_val:
            best_over_val, best_over_move = vfinal, (dx, dy)

    if best_over_move is None:
        return [0, 0]
    return [best_over_move[0], best_over_move[1]]