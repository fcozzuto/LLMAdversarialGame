def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]) - 0.35 * cheb(ox, oy, r[0], r[1]), r[0], r[1]))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        dist_term = -myd + 0.25 * opd

        # If moving lets opponent get strictly closer to the same target, penalize.
        opp_step_best = cheb(ox, oy, tx, ty)
        for odx, ody in dirs:
            jx, jy = ox + odx, oy + ody
            if 0 <= jx < w and 0 <= jy < h and (jx, jy) not in obstacles:
                opp_step_best = min(opp_step_best, cheb(jx, jy, tx, ty))
        # our next distances compared to opponent's next
        my_after = myd
        opp_after = opp_step_best
        contest_pen = 0.0
        if resources and opp_after < my_after:
            contest_pen = -1.2 * (my_after - opp_after)

        # Tie-breaker: reduce distance to opponent to allow contesting nearby resources.
        anti_opp = -0.08 * cheb(nx, ny, ox, oy)

        val = dist_term + contest_pen + anti_opp
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]