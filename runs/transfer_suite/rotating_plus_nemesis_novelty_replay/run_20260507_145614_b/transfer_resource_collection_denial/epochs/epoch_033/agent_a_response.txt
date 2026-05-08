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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # If already on a resource, stay
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    # Behavior change: "denial" targeting—prefer resources where we can beat the opponent,
    # and if none, move to disrupt by heading toward the opponent's nearest resource.
    opp_nearest = None
    best_tgt = None
    best_gap = -10**9

    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        gap = opd - myd  # positive means we are closer
        if gap > best_gap:
            best_gap = gap
            best_tgt = (rx, ry)
        if opp_nearest is None or cheb(ox, oy, rx, ry) < cheb(ox, oy, opp_nearest[0], opp_nearest[1]):
            opp_nearest = (rx, ry)

    # Decide target: if we can beat some resource (gap>0), go for the best gap;
    # otherwise, chase the opponent-nearest resource to contest quickly.
    target = best_tgt if best_gap > 0 else opp_nearest
    tx, ty = target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Value: minimize our distance to target, but also avoid moves that let opponent get closer
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Add penalty for stepping away from opponent-nearest when we're behind
        if best_gap <= 0:
            ax, ay = opp_nearest
            myd_opp = cheb(nx, ny, ax, ay)
            val = (myd * 10 + myd_opp, -opd)
        else:
            # Encourage shortening the winning gap
            val = (myd, -(opd - myd), cheb(nx, ny, ox, oy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]