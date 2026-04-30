def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Defensive: drift toward center to reduce opponent reachability
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = min(legal, key=lambda t: cheb(t[2], t[3], cx, cy))
        return [best[0], best[1]]

    # Prefer moves that create the largest distance advantage to some resource.
    res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res:
        return [0, 0]

    res_set = set(res)
    best_move = None
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        val = 0
        if (nx, ny) in res_set:
            val += 10**7  # immediate pickup priority
        # Choose the resource for which we maximize (opponent_dist - my_dist)
        # and lightly break ties by also preferring shorter my_dist.
        max_adv = -10**18
        best_myd = 10**18
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > max_adv or (adv == max_adv and myd < best_myd):
                max_adv = adv
                best_myd = myd
        # Encourage taking resources that are not too far even if adv is similar.
        val += max_adv * 1000 - best_myd
        # Slightly avoid moving directly toward opponent unless we gain advantage.
        my_to_opp = cheb(nx, ny, ox, oy)
        val += -my_to_opp * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]