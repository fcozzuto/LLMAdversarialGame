def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    tr = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Predict opponent target: nearest resource to them (ties: smallest coords)
    opp_target = None
    opp_best_d = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        d = man(ox, oy, tx, ty)
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (tx, ty) < opp_target):
            opp_best_d, opp_target = d, (tx, ty)

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by (a) advantage on the best rival-for-target resource,
        # (b) strongly avoiding the opponent's current target unless we can beat them decisively.
        local_best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) == 2):
                continue
            tx, ty = r[0], r[1]
            if not inb(tx, ty) or (tx, ty) in obs:
                continue
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            advantage = (do - ds)

            # If it's opponent's nearest target, penalize unless we win very clearly
            if opp_target is not None and (tx, ty) == opp_target:
                # Need a strong lead to justify contesting their target
                advantage -= 80
                if ds + 0 >= do:
                    advantage -= 40
                else:
                    advantage += 30

            # Time pressure: prefer resources we can reach well before opponent and within remaining turns
            time_term = 0
            if isinstance(tr, int) and tr > 0:
                time_term += (tr - ds) // 2
                time_term -= max(0, ds - tr) * 5

            sc = advantage * 20 - ds * 2 + time_term
            if local_best is None or sc > local_best:
                local_best = sc

        if local_best is None:
            continue
        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]