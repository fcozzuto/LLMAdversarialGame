def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = kdist(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
                bestv, best = v, [dx, dy]
        return best

    # Prefer cells that increase our capture likelihood over opponent.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Safety against diagonal_probe: avoid moving into tight approach lines.
        opp_close = kdist(nx, ny, ox, oy)
        safety = opp_close * 0.8

        # Interception: pick target resource where we can be strictly earlier than opponent.
        best_gap = -10**9
        for rx, ry in resources:
            myd = kdist(nx, ny, rx, ry)
            opd = kdist(ox, oy, rx, ry)
            gap = opd - myd  # positive means we get closer to it than opponent
            if gap > best_gap:
                best_gap = gap
                if best_gap >= 6:
                    break

        # Encourage moving toward the nearest resource too, but only if it doesn't help opponent.
        my_near = 10**9
        for rx, ry in resources:
            d = kdist(nx, ny, rx, ry)
            if d < my_near:
                my_near = d
        approach = -my_near * 0.12

        # Additional anti-stalemate: keep moving away from opponent when very close.
        retreat = 0.0
        if opp_close <= 2:
            retreat = (2 - opp_close) * 2.0

        # Combine: maximize capture advantage primarily, then safety/approach.
        v = best_gap * 5.0 + safety + approach + retreat

        if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
            bestv = v
            best = [dx, dy]

    return best