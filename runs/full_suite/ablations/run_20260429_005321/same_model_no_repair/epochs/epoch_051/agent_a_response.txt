def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best_res = None
    best_od = 10**18
    for rx, ry in resources:
        od = king_dist(ox, oy, rx, ry)
        if od < best_od:
            best_od = od
            best_res = (rx, ry)

    rx, ry = best_res
    sd = king_dist(sx, sy, rx, ry)
    can_race = sd <= best_od

    if can_race:
        tx, ty = rx, ry
    else:
        # Intercept/denial: head to midpoint of our position and their nearest resource.
        tx = (sx + rx) // 2
        ty = (sy + ry) // 2
        # If midpoint is blocked, aim one step closer to the resource direction.
        if (tx, ty) in obstacles:
            stepx = 0 if rx == sx else (1 if rx > sx else -1)
            stepy = 0 if ry == sy else (1 if ry > sy else -1)
            tx, ty = sx + stepx, sy + stepy
            tx = max(0, min(gw - 1, tx))
            ty = max(0, min(gh - 1, ty))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self_target = king_dist(nx, ny, tx, ty)
        d_opp_to_target = king_dist(ox, oy, tx, ty)
        d_opp_after = king_dist(ox, oy, nx, ny)

        if can_race:
            # Race win: prioritize reducing our distance to the true resource and widening gap.
            d_self_res = king_dist(nx, ny, rx, ry)
            d_opp_res = king_dist(ox, oy, rx, ry)
            val = (d_opp_res -