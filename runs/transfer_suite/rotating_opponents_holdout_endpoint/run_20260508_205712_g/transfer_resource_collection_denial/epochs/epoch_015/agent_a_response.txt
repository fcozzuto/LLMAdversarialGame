def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    my = (sx, sy)
    opp = (ox, oy)

    # Determine whether opponent is currently winning overall for a likely target,
    # then either contest (if they have an edge) or push a secure race (if we lead).
    best_need = -10**9  # max (opp_dist - self_dist) at current positions
    best_target = None
    for r in resources:
        if r in obstacles:
            continue
        dS = cheb(my, r)
        dO = cheb(opp, r)
        need = dO - dS
        if need > best_need or (need == best_need and (best_target is None or dS < cheb(my, best_target))):
            best_need, best_target = need, r

    contest = (best_need > 0)  # if positive, opponent is closer to some resource

    # Evaluate next step by future race outcome, penalize collisions/near-obstacles.
    best = (-10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my2 = (nx, ny)

        # obstacle proximity penalty (lightweight)
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    pen -= 1

        # choose resource with best objective from this move
        # If contesting: maximize (dO - dS) improvement (deny opponent).
        # Else: maximize (dO - dS) margin too, but prefer reaching closer.
        local_best = -10**18
        for r in resources:
            if r in obstacles:
                continue
            dS = cheb(my2, r)
            dO = cheb(opp, r)
            race = dO - dS  # positive means we are closer or tie
            if contest:
                val = race*50 - dS  # deny; also move toward it
            else:
                val = race*50 + (-dS) + (1 if dS < cheb(opp, r) else 0)
            if val > local_best or (val == local_best and dS < cheb(my2, r)):
                local_best = val

        # small tie-break: prefer staying closer to best_target if equal
        tb = 0
        if best_target is not None:
            tb = -cheb(my2, best_target)
        score = local_best + pen + tb
        if score > best[0]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]]