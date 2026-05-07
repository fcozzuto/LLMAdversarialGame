def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Opponent likely races: estimate their closest target and avoid it unless we can beat it.
    opp_best_d = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
    opp_close_thresh = opp_best_d

    best = None
    best_val = -10**30
    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue

            # Evaluate this move by best resource "race score"
            move_best = -10**30
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)

                # Main goal: collect quickly (low sd) while ensuring we are not far behind (od - sd not too small).
                race = od - sd  # positive means we are closer than opponent to that resource
                # If it's the opponent's likely closest, demand a stronger lead; otherwise accept slightly behind but faster.
                is_opp_target = od <= opp_close_thresh
                lead_bonus = race * (12 if is_opp_target else 7)

                # Penalize self distance strongly; secondary tie on lead, tertiary on opponent distance.
                val = lead_bonus - sd * (3 if is_opp_target else 2) + od * 0.02
                if val > move_best:
                    move_best = val

            if move_best > best_val:
                best_val = move_best
                best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]