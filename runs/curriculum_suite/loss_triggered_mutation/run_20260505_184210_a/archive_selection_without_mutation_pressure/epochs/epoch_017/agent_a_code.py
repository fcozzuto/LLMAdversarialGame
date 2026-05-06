def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        # Deterministic fallback: move to a corner-opposite line toward opponent
        tx, ty = (w - 1 if sx < (w - 1) / 2 else 0), (h - 1 if sy < (h - 1) / 2 else 0)
        best = None
        for dx, dy in legal:
            d = cheb(sx + dx, sy + dy, tx, ty)
            key = (d, cheb(sx + dx, sy + dy, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Interception heuristic: pick moves that maximize how much earlier we can get to some resource.
    # If we can't beat opponent anywhere, move to reduce opponent distance while maintaining resource proximity.
    best_move = None
    best_key = None
    res_sorted = sorted(resources, key=lambda p: cheb(ox, oy, p[0], p[1]))
    # Limit consideration to keep deterministic + fast
    res_sorted = res_sorted[:min(6, len(res_sorted))]

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_res_d = None
        for rx, ry in res_sorted:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage: positive means we are closer or equal to that resource than opponent.
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_res_d):
                best_adv = adv
                best_res_d = sd
        # If no positive advantage, shift focus to blocking (get closer to opponent) but don't abandon resources entirely.
        opp_d = cheb(nx, ny, ox, oy)
        # Primary: maximize advantage; Secondary: minimize our distance to the best resource; Tertiary: reduce opponent distance.
        key = (-best_adv, best_res_d, opp_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]