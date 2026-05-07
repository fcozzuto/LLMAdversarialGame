def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_cell = None
    alpha = 0.65  # prefer cells where we are closer than opponent

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        self_d = dsq(sx, sy, rx, ry)
        opp_d = dsq(ox, oy, rx, ry)
        # Prefer nearer to us; penalize if opponent is much nearer.
        # Tie-break by remaining distance (self_d).
        val = (self_d - alpha * opp_d, self_d, rx, ry)
        if best_cell is None or val < best_cell[0]:
            best_cell = (val, (rx, ry))
    if best_cell is None:
        return [0, 0]
    tx, ty = best_cell[1]

    # Choose move that gets us closer to the selected target, but also considers immediate advantage.
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cur_self = dsq(nx, ny, tx, ty)
        cur_opp_best = None
        # estimate "contested advantage" by nearest resource from opponent after our move
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dsq(ox, oy, rx, ry)
            if cur_opp_best is None or d < cur_opp_best:
                cur_opp_best = d
        if cur_opp_best is None:
            cur_opp_best = 0
        # primary: reduce distance to our target; secondary: increase relative advantage
        val = (cur_self, dsq(nx, ny, tx, ty) - alpha * cur_opp_best, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_move[0] is None or val < best_move[0]:
            best_move = (val, [dx, dy])

    if best_move[1] is None:
        return [0, 0]
    return best_move[1]