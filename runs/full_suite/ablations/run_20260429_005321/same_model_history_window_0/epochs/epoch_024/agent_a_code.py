def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if resources:
        for rx, ry in resources:
            if (sx, sy) == (rx, ry):
                return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_tx = None
    best_score = -10**9
    best_dist = 10**9

    def manh2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = manh2(sx, sy, rx, ry)
        do = manh2(ox, oy, rx, ry)
        lead = do - ds  # positive if we are closer
        tie = (ds < best_dist) or (ds == best_dist and (rx, ry) < best_tx)
        val = lead - ds * 0.0001
        if val > best_score or (val == best_score and tie):
            best_score = val
            best_dist = ds
            best_tx = (rx, ry)

    if best_tx is None:
        # No reachable resources: move to maximize distance from opponent deterministically.
        tx, ty = ox, oy
    else:
        tx, ty = best_tx

    ax = tx - sx
    ay = ty - sy
    want_dx = 0 if ax == 0 else (1 if ax > 0 else -1)
    want_dy = 0 if ay == 0 else (1 if ay > 0 else -1)

    def ok_cell(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Competition pressure: if opponent is also close to the target, we slightly avoid them.
    opp_to_target = manh2(ox, oy, tx, ty) if resources else manh2(ox, oy, sx, sy)
    my_to_target = manh2(sx, sy, tx, ty)
    avoid_opp = resources and opp_to_target <= my_to_target

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok_cell(nx, ny):
            continue
        d_to_t = manh2(nx, ny, tx, ty)
        d_opp = manh2(nx, ny, ox, oy)
        # Primary: go to target; Secondary: avoid opponent when competing; Tertiary: prefer moves aligning to direction.
        align = -((dx - want_dx) * (dx - want_dx) + (dy - want_dy) * (dy - want_dy))
        val = -d_to_t + 0.001 * align
        if avoid_opp:
            val += 0.0005 * d_opp
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]