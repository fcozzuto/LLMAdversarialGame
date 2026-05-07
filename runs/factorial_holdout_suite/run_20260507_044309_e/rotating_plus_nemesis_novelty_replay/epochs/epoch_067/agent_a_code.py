def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(r) for r in res if isinstance(r, (list, tuple)) and len(r) == 2)

    # Pick a small deterministic set of promising targets
    best_targets = []
    for rx, ry in res_set:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        best_targets.append((adv, -ds, rx, ry))
    if not best_targets:
        return [0, 0]
    best_targets.sort(key=lambda t: (t[0], t[1], t[2], t[3]), reverse=True)
    targets = best_targets[:3]

    opp_d_now = cheb(ox, oy, targets[0][2], targets[0][3])
    best_move = (0, 0)
    best_score = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate gain
        immediate = 1 if (nx, ny) in res_set else 0

        # Consider the best target under this move
        move_best_adv = -10**9
        move_best_do_minus_ds = -10**9
        move_best_ds = 10**9
        for _, _, tx, ty in targets:
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            adv2 = do2 - ds2
            if adv2 > move_best_adv or (adv2 == move_best_adv and ds2 < move_best_ds):
                move_best_adv = adv2
                move_best_do_minus_ds = adv2
                move_best_ds = ds2

        opp_d_after = cheb(ox, oy, targets[0][2], targets[0][3])
        opp_push = opp_d_now - opp_d_after  # usually 0 unless target changes notionally; kept for determinism

        # Score weights: prioritize taking resources, then winning the closest contest, then improving our distance
        score = immediate * 10000 + move_best_do_minus_ds * 100 + (-move_best_ds) * 2 + opp_push
        if score > best_score or (score == best_score and (dxm, dym) < best_move):
            best_score = score
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]