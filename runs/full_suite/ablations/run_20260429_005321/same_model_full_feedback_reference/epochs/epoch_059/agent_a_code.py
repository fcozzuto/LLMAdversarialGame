def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources, flee to maximize distance from opponent.
    if not resources:
        best = (-(10**18), 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = d2(nx, ny, ox, oy)
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best_val = -(10**18)
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_best = -(10**18)
        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)

            # Favor resources where we are (or will be) competitive vs opponent.
            # Opponent closer => penalize heavily.
            gap = opd - myd
            val = gap * 10 - myd - abs(rx - nx) - abs(ry - ny)

            # Avoid moving too close to opponent unless it helps contest a resource.
            val -= (d2(nx, ny, ox, oy) < 4) * 50

            if val > my_best:
                my_best = val

        # Minor preference for staying on a good local direction (reduce my distance to the best target).
        # Deterministic tie-break via lexicographic move order already fixed by deltas.
        if my_best > best_val:
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]