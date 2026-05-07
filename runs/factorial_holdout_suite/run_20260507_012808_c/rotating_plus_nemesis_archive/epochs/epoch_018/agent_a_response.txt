def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def cell_score(px, py, rx, ry):
        my_d = cheb(px, py, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        row_gap = abs(ry - oy)
        # Prefer being closer than opponent; also prefer rows where opponent is less likely to sweep into.
        return my_d - opp_d - 0.03 * row_gap

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in occ:
            continue
        val = 10**18
        for rx, ry in resources:
            s = cell_score(nx, ny, rx, ry)
            # Add slight preference for closer raw distance to avoid stalling.
            d = cheb(nx, ny, rx, ry)
            if s + 0.01 * d < val:
                val = s + 0.01 * d
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]