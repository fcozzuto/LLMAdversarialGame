def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = {(p[0], p[1]) for p in obstacles}

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None  # (score, -my_best, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_pick = None
        my_best_d = 10**9
        opp_for_my = 0
        # 1-step lookahead: choose the resource that gives maximal lead from nx,ny
        for rx, ry in resources:
            my_d = king_dist(nx, ny, rx, ry)
            op_d = king_dist(ox, oy, rx, ry)
            lead = op_d - my_d  # positive => I'm closer
            if my_pick is None or lead > my_pick or (lead == my_pick and my_d < my_best_d):
                my_pick = lead
                my_best_d = my_d
                opp_for_my = op_d
        # Prefer higher lead; if tied, faster capture; if still tied, move closer to opponent (interceptor)
        intercept = king_dist(nx, ny, ox, oy)
        score = (my_pick, -my_best_d, -intercept, nx, ny)
        if best is None or score > best[0]:
            best = (score, [dx, dy])

    return best[1]