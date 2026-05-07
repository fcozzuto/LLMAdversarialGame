def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(a, b, c, d):
        return max(abs(c - a), abs(d - b))  # Chebyshev

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    # Two-stage deterministic evaluation:
    # 1) Prefer resources where we are strictly closer than opponent.
    # 2) If none, minimize opponent advantage while still progressing to some resource.
    best_move = None
    best_val = None

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_self_adv = None  # maximum (opp_d - self_d) among strictly ahead targets
        best_fallback = None  # best score when no strictly ahead target exists

        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            if adv > 0:
                # Prefer larger advantage, then closer self distance (faster collection)
                key = (adv, -ds)
                if best_self_adv is None or key > best_self_adv:
                    best_self_adv = key
            else:
                # Penalize being behind; still progress by preferring smaller ds and smaller do
                # (more likely to "arrive first" later)
                key = (adv, -ds, -do)
                if best_fallback is None or key > best_fallback:
                    best_fallback = key

        if best_self_adv is not None:
            val = (1, best_self_adv[0], best_self_adv[1])  # stage 1 wins
        else:
            # stage 2
            if best_fallback is None:
                val = (0, -999999, 0)
            else:
                val = (0, best_fallback[0], best_fallback[1])

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]