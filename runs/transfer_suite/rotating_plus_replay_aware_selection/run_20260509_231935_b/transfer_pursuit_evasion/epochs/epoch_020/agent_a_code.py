def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr) and "purs" in orr:
        self_is_pursuer = False
    if ("evad" in sr) and ("purs" not in sr):
        self_is_pursuer = False
    if ("purs" in sr) and ("evad" in sr):
        self_is_pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    # Deterministic tie-breaking: fixed order of deltas, plus secondary score terms.
    best_move = [0, 0]
    best_score = -10**9 if self_is_pursuer else 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)  # Manhattan; diagonal allowed but capture radius is 0
        mob = mobility(nx, ny)

        # Additional penalty for moving into "near obstacle traps" while evading.
        adj_obs = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) in obs:
                adj_obs += 1

        if self_is_pursuer:
            # Chase: reduce distance; prefer higher mobility to avoid getting boxed.
            score = (-d) + 0.2 * mob - 0.05 * adj_obs
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # Evade: maximize distance; keep mobility and avoid obstacle adjacency.
            score = (d) + 0.2 * mob - 0.1 * adj_obs
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]