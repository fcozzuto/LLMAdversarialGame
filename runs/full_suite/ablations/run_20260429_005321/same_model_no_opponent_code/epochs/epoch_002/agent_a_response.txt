def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_t = None
    best_sc = -10**18
    # Target: prioritize where we are closer than opponent (to steal / secure).
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            sc = 10**9
        else:
            # Encourage being closer; also prefer nearer absolute distance once tie.
            sc = (do - ds) * 100 - ds
            # If we can't get it sooner than opponent, reduce but still consider as blocker.
            if do - ds < -1:
                sc -= (abs(do - ds) * 10)
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    # Choose step that reduces distance to target; avoid obstacles and boundaries.
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = -10**18

    # Also discourage running into squares where opponent can immediately get closer to the same target.
    opp_cur_d = cheb(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)

        # Opponent "pressure": if opponent is very likely to get closer next step, slightly prefer safer moves.
        # Predict opponent step toward target (deterministically choose best among their deltas).
        opp_best_d = opp_cur_d
        for odx, ody in moves:
            mx, my = ox + odx, oy + ody
            if not inb(mx, my) or (mx, my) in obstacles:
                continue
            md = cheb(mx, my, tx, ty)
            if md < opp_best_d:
                opp_best_d = md

        # Valuing: prioritize reduced distance to target and avoid giving opponent a big advantage.
        val = (cur_d - d) * 1000 - d
        val -= max(0, (opp_best_d - (opp_cur_d - 0))) * 5

        # Small tie-break: prefer moves that advance in x then y deterministically.
        val += (-abs(dx) - abs(dy)) * 0.1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]