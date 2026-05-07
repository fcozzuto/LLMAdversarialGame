def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 3 if sx > (gw - 1) // 2 else (4 if sx < (gw - 1) // 2 else sx)
        ty = 3 if sy > (gh - 1) // 2 else (4 if sy < (gh - 1) // 2 else sy)
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a resource we can realistically secure (or move to one that increases our lead).
    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_me  # positive means we are closer
        # Prefer positive lead and closeness; if none positive, prefer biggest lead.
        val = lead * 100 - d_me
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_me2 = cheb(nx, ny, rx, ry)
        d_opp2 = cheb(ox, oy, rx, ry)
        lead2 = d_opp2 - d_me2
        # Small bonus for moving to improve overall contest among all resources.
        best_future = -10**18
        for r2 in resources:
            rr_x, rr_y = r2
            dm = cheb(nx, ny, rr_x, rr_y)
            do = cheb(ox, oy, rr_x, rr_y)
            best_future = max(best_future, (do - dm) * 10 - dm)
        score = lead2 * 100 - d_me2 * 2 + best_future
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move