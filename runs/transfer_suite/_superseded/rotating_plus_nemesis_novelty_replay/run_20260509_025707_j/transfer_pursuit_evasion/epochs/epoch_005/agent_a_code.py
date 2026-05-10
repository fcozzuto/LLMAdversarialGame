def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def norm_pos(p):
        try:
            x, y = p
            return int(x), int(y)
        except Exception:
            return None

    sp = norm_pos(observation.get("self_position"))
    op = norm_pos(observation.get("opponent_position"))
    if sp is None or op is None:
        return [0, 0]
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for o in observation.get("obstacles") or []:
        q = norm_pos(o)
        if q is not None:
            obstacles.add(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = observation.get("self_role") or "pursuer"
    is_evader = (str(role).lower() == "evader")

    # Greedy horizon-1 with obstacle-aware tie-breakers.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        # Prefer motion for evader too; staying is allowed but penalized unless forced.
        stay_pen = 0 if (dx == 0 and dy == 0) else 0.1

        if is_evader:
            # Maximize distance; also prefer moving toward the farther corner relative to pursuer.
            target_x = w - 1 if nx <= (w - 1 - nx) else 0  # deterministic choice based on position
            target_y = h - 1 if ny <= (h - 1 - ny) else 0
            corner_adv = abs(nx - target_x) + abs(ny - target_y)
            score = man * 10.0 + corner_adv * 0.01 - stay_pen
            # If moving would reduce distance too much, discourage.
            cur_man = abs(sx - ox) + abs(sy - oy)
            if man < cur_man:
                score -= (cur_man - man) * 2.0
        else:
            # Pursuer: minimize distance; also avoid getting boxed in by obstacles.
            # "Freedom" counts open neighboring cells after the move.
            freedom = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    freedom += 1
            score = -man * 10.0 + freedom * 0.2 + stay_pen
            # Encourage moving when it helps.
            cur_man = abs(sx - ox) + abs(sy - oy)
            if man > cur_man:
                score -= (man - cur_man) * 3.0

        if best_score is None or (score > best_score):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]