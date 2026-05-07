def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = (gw - 1) // 2
        ty = (gh - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick the resource where we can arrive first (or disrupt the opponent most).
    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Resource-denier opponent: maximize distance advantage; prefer closer wins if competitive.
        val = (d_opp - d_me) * 10 - d_me
        if d_me == 0:
            val += 10**6
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) == (rx, ry):
            v = 10**9
        else:
            d_me2 = cheb(nx, ny, rx, ry)
            d_opp2 = cheb(ox, oy, rx, ry)
            # If we can still beat them soon, prioritize; otherwise keep pressure by reducing their lead.
            v = (d_opp2 - d_me2) * 10 - d_me2
            # Slight bias: move generally towards target to avoid oscillation.
            v += -0.1 * (abs(nx - rx) + abs(ny - ry))
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best