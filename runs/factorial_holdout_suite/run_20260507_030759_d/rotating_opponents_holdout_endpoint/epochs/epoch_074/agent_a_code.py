def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def approx_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(x, y, tx, ty):
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            nd = approx_dist(nx, ny, tx, ty)
            # Prefer smaller distance; slight preference for diagonal if it helps.
            diag_bonus = 1 if dx != 0 and dy != 0 else 0
            score = -nd * 100 - (dx == 0 and dy == 0) * 5 + diag_bonus
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Choose a resource where we have timing advantage; otherwise still pick nearest.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        myd = approx_dist(sx, sy, rx, ry)
        opd = approx_dist(ox, oy, rx, ry)
        if myd == 0:
            return [0, 0]
        # If we can arrive no later, prioritize; else deprioritize but keep options.
        advantage = opd - myd
        val = (1 if myd <= opd else 0) * 10**6 + advantage * 2000 - myd * 3 - (rx + ry) * 0.01
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r

    # Obstacle-aware local detour: if direct toward target is blocked, step_toward handles it.
    move = step_toward(sx, sy, rx, ry)

    # Micro-avoid: if opponent is adjacent to that resource and we are far, redirect toward nearest "contested-free" one.
    if resources:
        myd = approx_dist(sx, sy, rx, ry)
        opd = approx_dist(ox, oy, rx, ry)
        if opd <= 1 and myd >= 2:
            best_r2 = None
            best_val2 = -10**18
            for rx2, ry2 in resources:
                myd2 = approx_dist(sx, sy, rx2, ry2)
                opd2 = approx_dist(ox, oy, rx2, ry2)
                if myd2 == 0:
                    return [0, 0]
                # Prefer options where opponent is not immediately there.
                val2 = (opd2 > 1) * 10**6 + (opd2 - myd2) * 1500 - myd2 * 4
                if val2 > best_val2:
                    best_val2 = val2
                    best_r2 = (rx2, ry2)
            if best_r2 is not None:
                move = step_toward(sx, sy, best_r2[0], best_r2[1])

    return [int(move[0]), int(move[1])]