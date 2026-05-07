def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = (None, -10**18)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        move_best_score = -10**18
        move_best_dist = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Collect immediately if possible
            if nx == rx and ny == ry:
                score = 10**9 + 1000
            else:
                # Prefer resources where we are closer than opponent
                adv = do - ds
                # Encourage lower ds, penalize giving the opponent strong advantage
                score = adv * 200 - ds * 5 + (ds == 0) * 100000
            # Secondary: choose tighter route to the best scoring resource
            if score > move_best_score or (score == move_best_score and ds < move_best_dist):
                move_best_score = score
                move_best_dist = ds

        # Extra: if staying puts us adjacent/closer to current best, slightly reward movement that reduces our distance
        # (helps break symmetric ties deterministically)
        score2 = move_best_score - man(nx, ny, sx, sy) * 0  # no-op, keep deterministic structure

        cand = (mx, my)
        if score2 > best[1]:
            best = (cand, score2)
        elif score2 == best[1]:
            # deterministic tie-breaker: prefer larger dx, then larger dy
            if cand[0] > best[0][0] or (cand[0] == best[0][0] and cand[1] > best[0][1]):
                best = (cand, score2)

    return [int(best[0][0]), int(best[0][1])]