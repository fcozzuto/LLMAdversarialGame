def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose a resource where we can gain tempo over the opponent.
    if resources:
        best_res = None
        best_gap = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive means we're closer
            if best_gap is None or gap > best_gap or (gap == best_gap and sd < best_res[0]):
                best_gap = gap
                best_res = (sd, rx, ry)
        target = (best_res[1], best_res[2])
    else:
        # No visible resources: drift toward center.
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        new_sd = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Prefer increasing our advantage; small preference to move away from opponent.
        val = (opp_d - new_sd) * 100 - new_sd + cheb(nx, ny, ox, oy) * 0.05
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]