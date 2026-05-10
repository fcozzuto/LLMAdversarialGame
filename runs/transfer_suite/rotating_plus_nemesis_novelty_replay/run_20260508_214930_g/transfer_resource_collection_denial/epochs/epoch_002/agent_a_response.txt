def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles_list = observation.get('obstacles', []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource: prefer ones we can reach no later than opponent; if none, pick smallest disadvantage.
    best = None
    target = resources[0]
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = opp_d - self_d  # positive => we are closer or tied
        # Tie-break: earlier pickup, then more "cornered" toward our side (deterministic)
        score = (diff, -self_d, rx + ry, rx * 3 - ry)
        if best is None or score > best:
            best = score
            target = (rx, ry)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)

        # Secondary safety: prefer not to step into squares where opponent would immediately be much closer to the same target.
        opp_d_next = cheb(ox, oy, tx, ty)
        # (Opponent position doesn't change this turn; this term keeps behavior stable while still deterministic.)
        # Add a slight bias away from opponent to reduce races on contested spots.
        dist_opp = cheb(nx, ny, ox, oy)

        # Higher is better
        val = (-d_to, dist_opp, -abs(tx - nx) - abs(ty - ny), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]