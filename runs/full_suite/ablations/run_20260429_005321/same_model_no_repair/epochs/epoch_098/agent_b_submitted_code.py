def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]

    def local_obst_pen(x, y):
        p = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + ddx, y + ddy) in obst:
                p += 2
        for ddx, ddy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                p += 1
        return p

    # Choose target resource by relative advantage: myDist - oppDist (smaller is better)
    best_target = None
    best_rel = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        rel = myd - opd
        if best_rel is None or rel < best_rel or (rel == best_rel and myd < cheb(sx, sy, best_target[0], best_target[1])):
            best_rel = rel
            best_target = (rx, ry)

    if best_target is None:
        # No resources: keep distance from opponent and avoid obstacles
        target_x, target_y = w - 1 - ox, h - 1 - oy
    else:
        target_x, target_y = best_target

    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Resource drive
        myd = cheb(nx, ny, target_x, target_y)
        oppd = cheb(nx, ny, ox, oy)

        # Relative progress to target (prefer getting closer; if already close, go still/keep)
        if best_target is None:
            res_term = -cheb(nx, ny, target_x, target_y)
        else:
            res_term = -myd

        # Opponent pressure: avoid letting them get too close; also discourage being in their immediate neighborhood
        opp_term = 0
        if oppd <= 1:
            opp_term -= 50
        opp_term += oppd * 2

        # Obstacles
        obst_term = -local_obst_pen(nx, ny)

        # Tie-breakers: prefer moves that reduce cheb distance to target, then deterministic order by dx,dy
        val = res_term + opp_term + obst_term
        if best_val is None or val > best_val or (val == best_val and (myd, local_obst_pen(nx, ny), dx, dy) < (cheb(best_move[2], best_move[3], target_x, target_y), local_obst_pen(best_move[2], best_move[3]), best_move[0], best_move[1])):
            best_val =