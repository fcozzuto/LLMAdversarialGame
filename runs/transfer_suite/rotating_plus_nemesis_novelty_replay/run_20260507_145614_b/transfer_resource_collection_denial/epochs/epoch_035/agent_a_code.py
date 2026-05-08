def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

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

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; tie-break by shorter time and then position
        key = (myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_val = -10**18

    opp_cur_dist = cheb(ox, oy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # Value: reduce our distance, and if we can reach at least as fast as opponent, prefer it.
        lead_now = cheb(sx, sy, tx, ty) - opp_cur_dist
        lead_after = myd2 - opp_cur_dist
        # Large weight on closing distance; extra if we don't fall behind.
        val = (-myd2 * 100) + (200 if lead_after <= lead_now else 0) - (abs(nx - tx) + abs(ny - ty))
        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_m):
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]