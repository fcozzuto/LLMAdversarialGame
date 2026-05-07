def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_r = None
    best_val = 10**18
    opp_adj = cheb(ox, oy, sx, sy) <= 1

    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Effective priority: prefer being closer; strongly discourage resources opponent is racing to.
        race_pen = 0
        if opp_d < my_d:
            race_pen = 4 * (my_d - opp_d)
        # Mild tie-break: if opponent is near, avoid feeding him nearby by preferring resources farther from him.
        opp_dist_bonus = 0 if not opp_adj else 0.2 * opp_d
        val = my_d + race_pen + opp_dist_bonus
        if val < best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r

    # Choose a feasible move that reduces distance to target; tie-break by increasing distance from opponent.
    best_move = [0, 0]
    best_t = 10**18
    best_opp = -1
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in occ:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        if d_t < best_t or (d_t == best_t and d_o > best_opp):
            best_t = d_t
            best_opp = d_o
            best_move = [dx, dy]

    return best_move