def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources we can reach before opponent; else closest we can still grab.
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Use turn_index to slightly break ties deterministically.
            t = observation.get("turn_index", 0)
            # If we arrive not later than opponent, prioritize; otherwise deprioritize but keep option.
            arrive_win = 0 if ds <= do else 1
            # Smaller ds better; if ds equal, larger (do-ds) better; then deterministic by position and time.
            key = (arrive_win, ds, -(do - ds), (rx * 8 + ry), t % 3)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)

    # Move that minimizes distance to chosen target, while avoiding "giving" a nearer resource next step.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds1 = cheb(nx, ny, tx, ty)

        # Secondary check: ensure the opponent isn't one step from a resource we ignore.
        # Compute minimal opponent distance to any resource; smaller is worse for us.
        min_do = 10**9
        if resources:
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = cheb(ox, oy, rx, ry)
                if d < min_do:
                    min_do = d
        # Prefer taking the resource race: also prefer moves that reduce our lead gap vs opponent.
        # Lead gap: opponent_distance - our_distance (positive is good).
        do_t = cheb(ox, oy, tx, ty)
        lead = do_t - ds1

        key = (0 if legal(nx, ny) else 1, ds1, -lead, min_do, (nx * 8 + ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]