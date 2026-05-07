def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    cx, cy = w // 2, h // 2

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_mv = [0, 0]
    best_key = None

    # Pre-filter reachable resources for tie-breaking deterministically by coordinate.
    res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res:
        # Drift to center while staying valid.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                key = (cheb(nx, ny, cx, cy), nx, ny)
                if best_key is None or key < best_key:
                    best_key = key
                    best_mv = [dx, dy]
        return best_mv

    # Evaluate each candidate move by how much it improves my lead vs opponent on a few best resources.
    # Deterministic: only consider top 4 by current opponent distance.
    res_sorted = sorted(res, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    res_top = res_sorted[:4]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # My potential: maximize lead; break ties by getting closer to center and avoiding giving up lead.
        val = 0
        worst = 10**9
        for rx, ry in res_top:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => I arrive earlier
            # Emphasize immediate lead; also penalize being behind strongly.
            val += (lead * 10) - ds
            if ds - do > worst:
                worst = ds - do

        # Add small center preference to avoid dithering.
        center = cheb(nx, ny, cx, cy)
        key = (-val, worst, center, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = [dx, dy]

    return best_mv