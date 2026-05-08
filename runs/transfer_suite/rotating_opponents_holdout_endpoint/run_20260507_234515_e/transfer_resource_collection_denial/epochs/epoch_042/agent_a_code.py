def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a if a >= b else b

    # If no visible resources, move toward the middle of the board while staying away from obstacles.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # obstacle proximity penalty
            prox = 0
            for ax, ay in obstacles:
                if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                    prox = 1
                    break
            dist = abs(nx - tx) + abs(ny - ty)
            key = (dist + 2 * prox, cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: prefer resources we're closer to than opponent, and that we can reach soon.
    # Also make a one-step look so we don't step into obstacle-adjacent congestion.
    alpha = 1.2  # opponent closeness weight
    beta = 0.15  # slight bias to nearer resource for tempo
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # discourage moving into obstacle-adjacent squares
        near_obs = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near_obs = 1
                break

        # evaluate best resource from this candidate next position
        local_best = None
        local_best_key = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            score_adv = (d_opp - alpha * d_self)  # higher is better
            tempo = beta * d_self
            # tie-break deterministically by coordinates
            key = (-score_adv + tempo, rx, ry)
            if local_best_key is None or key < local_best_key:
                local_best_key = key
                local_best = score_adv

        # prefer moves that maximize advantage; if tied, prefer not-near obstacles and then smaller distance to opponent
        # Incorporate turn_index to break rare symmetries deterministically.
        ti = observation.get("turn_index", 0)
        key2 = (near_obs, local_best_key[0], cheb(nx, ny, ox, oy), (nx + w * ny + ti) % 7, dx, dy)
        if best_key is None or key2 < best_key:
            best_key = key2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]