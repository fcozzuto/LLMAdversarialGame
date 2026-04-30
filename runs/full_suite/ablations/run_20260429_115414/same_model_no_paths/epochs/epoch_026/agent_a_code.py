def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, just drift toward opponent's corner-ish to avoid getting blocked.
    if not resources:
        tx, ty = 7 if sx <= 3 else 0, 7 if sy <= 3 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        # fallback: try any valid move that doesn't go into obstacles
        best = None
        bestd = None
        for mx, my in dirs:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                d = abs(tx - nx) + abs(ty - ny)
                if best is None or d < bestd:
                    best, bestd = [mx, my], d
        return best if best is not None else [0, 0]

    # Evaluate each candidate step by maximizing advantage over opponent across all remaining resources.
    best_step = [0, 0]
    best_val = None
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        my_best = -10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Big weight on being closer than opponent (denial), mild penalty for longer travel.
            val = (opd - myd) * 20 - myd
            if val > my_best:
                my_best = val

        # Tie-break: prefer moves that reduce our distance to the best-rated resource (more decisive).
        if best_val is None or my_best > best_val:
            best_val = my_best
            best_step = [mdx, mdy]
        elif my_best == best_val:
            # deterministic tie-break: lexicographic preference toward reducing x then y
            if (mdx, mdy) < (best_step[0], best_step[1]):
                best_step = [mdx, mdy]

    return [int(best_step[0]), int(best_step[1])]