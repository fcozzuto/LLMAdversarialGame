def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    def best_resource(fromx, fromy):
        best = None
        bestv = -10**18
        for rx, ry in resources:
            d = dist(fromx, fromy, rx, ry)
            v = -d
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        bx, by = tx, ty
    else:
        opp_t = best_resource(ox, oy)
        best = None
        bestv = -10**18
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer cells where we have an advantage in reach, but strongly avoid the one the opponent is closest to.
            v = (od - sd) * 64 - sd
            if opp_t is not None and (rx, ry) == opp_t:
                v -= 10**6
            if v > bestv:
                bestv = v
                best = (rx, ry)
        bx, by = best if best is not None else resources[0]

    # Move one step toward chosen target (deterministic), accounting for legality.
    bestmv = (0, 0)
    bestd = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist(nx, ny, bx, by)
        # Secondary tie-break: stay closer to chosen target than opponent (race advantage)
        adv = dist(ox, oy, bx, by) - d
        key = (d, -adv, dx, dy)
        if key < (bestd, -10**18, 10, 10):
            bestd = d
            bestmv = (dx, dy)
        if d == bestd:
            if -adv > (dist(ox, oy, bx, by) - dist(sx + bestmv[0], sy + bestmv[1], bx, by)):
                bestmv = (dx, dy)
    return [int(bestmv[0]), int(bestmv[1])]