def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    # Evaluate moves by best resource we can "secure" from next position.
    # Score: strongly prefer states where we reach closer than opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = x, y
            dx, dy = 0, 0

        cur_best = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Immediate preference for adjacent collection.
            adj_bonus = 0
            if myd == 0:
                adj_bonus = 1000000
            elif myd == 1:
                adj_bonus = 2500
            elif myd == 2:
                adj_bonus = 250

            # If we're strictly closer, boost; if behind, penalize.
            closer_bonus = 0
            diff = opd - myd  # positive => we closer
            if diff > 0:
                closer_bonus = 800 * diff
            elif diff == 0:
                closer_bonus = -50
            else:
                closer_bonus = 250 * diff  # negative

            # Tie-break: shorter our distance; also avoid handing opponent immediate captures.
            hand_penalty = 0
            if opd <= 1 and myd > 1:
                hand_penalty = -300

            val = adj_bonus + closer_bonus - 10 * myd + hand_penalty
            if val > cur_best:
                cur_best = val

        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
        elif cur_best == best_val:
            # Deterministic tie-break: lexicographic by move preference order (given list order already deterministic).
            pass

    return [int(best_move[0]), int(best_move[1])]