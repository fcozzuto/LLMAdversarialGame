def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_tx, best_ty = None, None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # bigger is better for us
        # Prefer big advantage; then smaller our distance; then prefer resource closer to opponent (cuts their options).
        key = (-adv, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    tx, ty = best_tx, best_ty
    curd_self = cheb(sx, sy, tx, ty)
    curd_opp = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd_self = cheb(nx, ny, tx, ty)
        nd_opp = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Primary: improve our lead at target; Secondary: reduce our distance; Tertiary: move to increase distance from opponent to reduce interference.
        lead = nd_opp - nd_self
        inter = cheb(nx, ny, ox, oy)
        val = (-lead, nd_self, -inter)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    # If for some reason no valid move (shouldn't happen), stay.
    if best_val is None:
        return [0, 0]
    return best_move