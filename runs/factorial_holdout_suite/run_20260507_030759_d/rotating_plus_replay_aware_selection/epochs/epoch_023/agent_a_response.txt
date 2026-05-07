def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = [0, 0]
    best_score = -10**30
    best_spread = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        cur_best = -10**30
        cur_spread = -10**30
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            if ds == 0 and (nx, ny) == (rx, ry):
                score = 10**12
            else:
                # Strongly race for resources; also prefer states where we're closer than opponent.
                lead = do - ds
                score = lead * 2000 + (do - ds) * 20 - ds
                if lead > 0:
                    score += 5000  # extra commitment if we're ahead
                elif lead == 0:
                    score += 200  # slightly prefer tie-to-collection over falling behind

            # Keep best resource score for this move, and the "spread" for tie-breaking.
            if score > cur_best:
                cur_best = score
            spread = (do - ds) * 100 - ds
            if spread > cur_spread:
                cur_spread = spread

        # Prefer higher score; if close, prefer more spread (keeps more races favorable).
        if cur_best > best_score or (cur_best == best_score and cur_spread > best_spread):
            best_score = cur_best
            best_spread = cur_spread
            best = [dx, dy]

    # Fallback: deterministic nearest-resource step if all scoring paths somehow fail.
    if best_score <= -10**20:
        tx, ty = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if ok(sx + dx, sy + dy):
            return [dx, dy]
        if ok(sx + dx, sy):
            return [dx, 0]
        if ok(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    return best