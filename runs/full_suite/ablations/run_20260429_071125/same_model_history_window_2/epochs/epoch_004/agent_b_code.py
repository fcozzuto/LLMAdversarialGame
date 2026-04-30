def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # In absence of resources, press toward the side that reduces distance to opponent
            key = (md(nx, ny, ox, oy), abs(dx) + abs(dy), dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]] if best is not None else [0, 0]

    opp_cur = md(sx, sy, ox, oy)
    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        our_to_res_best = None
        adv_best = None
        for rx, ry in resources:
            ourd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            adv = oppd - ourd  # higher is better
            if adv_best is None or adv > adv_best or (adv == adv_best and (our_to_res_best is None or ourd < our_to_res_best)):
                adv_best = adv
                our_to_res_best = ourd

        # Encourage moving to a resource where we are ahead; also avoid drifting too far behind in global chase
        score = (adv_best if adv_best is not None else -10**9)
        # Anti-stall / minimal-distance to any resource after move
        min_our = None
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if min_our is None or d < min_our:
                min_our = d
        chase_pen = 0.05 * md(nx, ny, ox, oy)
        chase_bonus = -0.02 * (md(nx, ny, ox, oy) - opp_cur)  # slight preference not to increase distance
        key = (-score, min_our, chase_pen + chase_bonus, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]