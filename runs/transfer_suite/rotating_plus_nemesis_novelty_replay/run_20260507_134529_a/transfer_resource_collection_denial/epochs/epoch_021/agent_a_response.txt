def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target resource to maximize our chance to be first (arrive no later than opponent).
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        diff = myd - opd  # <=0 means we are at least as close in time
        # Primary: smallest diff (most likely to beat), then prefer larger advantage in our favor,
        # then prefer closer overall to reduce exposure.
        key = (diff, -((opd - myd)), myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry, myd, opd)

    if not best:
        return [0, 0]
    tx, ty, _, _ = best

    # If we can beat: move to reduce distance to (tx,ty).
    # If not: move to create the biggest improvement in (myd - opd) for this target.
    cur_my = cheb(sx, sy, tx, ty)
    cur_opd = cheb(ox, oy, tx, ty)
    cur_diff = cur_my - cur_opd

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        diff = myd - cur_opd
        # If we are behind, prefer reducing diff; if tied/leading, prefer reducing myd.
        lead = 1 if cur_diff <= 0 else 0
        key = (lead, abs(diff), diff, myd, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    # Final deterministic fallback if all moves invalid (shouldn't happen).
    return [int(best_m[0]), int(best_m[1])]