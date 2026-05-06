def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def one_step_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda d: (abs(d[0]) + abs(d[1]), d[1], d[0]))

    def cell_score(tx, ty, px, py):
        d_me = abs(tx - px) + abs(ty - py)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        # Encourage taking closer-to-us targets that opponent finds farther
        return lead * 1000 - d_me

    def best_target(px, py):
        best = None
        bestv = None
        for tx, ty in resources:
            v = cell_score(tx, ty, px, py)
            if best is None or v > bestv or (v == bestv and (abs(tx - px) + abs(ty - py), tx, ty) < (bestv_bd, besttx, bestty)):
                best = (tx, ty)
                bestv = v
                besttx, bestty = tx, ty
                bestv_bd = abs(tx - px) + abs(ty - py)
        return best, bestv

    best_move = (0, 0)
    best_move_val = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or one_step_blocked(nx, ny):
            continue
        _, tv = best_target(nx, ny)
        # Small preference for advancing towards the best target
        cur_best, _ = best_target(x, y)
        adv = 0
        if cur_best is not None:
            adv = (abs(cur_best[0] - x) + abs(cur_best[1] - y)) - (abs(cur_best[0] - nx) + abs(cur_best[1] - ny))
        val = tv + adv * 5 + (dx == 0 and dy == 0) * -1
        if best_move_val is None or val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]