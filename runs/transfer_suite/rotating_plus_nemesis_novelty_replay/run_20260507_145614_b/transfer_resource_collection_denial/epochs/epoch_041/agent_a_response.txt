def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    has_pos = False
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        local_best = -10**18
        local_has = False
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gain = opd - myd  # >0 means I'm closer right now
            if gain > 0:
                local_has = True
                # Prefer winning/resources with smaller distance; slight bias away from ties
                val = gain * 1000 - myd - 0.5 * (myd == opd)
            else:
                # If can't win immediately, pick nearer resources; still prefer those opponent is farther from
                val = (gain * 50) - myd
            if val > local_best:
                local_best = val
        if local_has:
            has_pos = True
        # If any move can secure a "closer-than-opponent" target, ignore non-winning moves.
        if has_pos and not any(cheb(sx + dxm, sy + dym, rx, ry) < cheb(ox, oy, rx, ry) for rx, ry in resources):
            continue
        if local_best > best_val:
            best_val = local_best
            best = (dxm, dym)

    return [int(best[0]), int(best[1])]