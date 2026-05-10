def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        # diagonal allowed: Chebyshev reflects fastest movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def clearance(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if legal(nx, ny):
                    c += 1
        return c

    sr = (observation.get("self_role") or "").lower()
    pr = "pursuer" in sr
    # If unknown, default to evader behavior which tends to survive longer in wall-run archetype.
    pursuer = pr

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    if pursuer:
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), (ox, oy))
            # Prefer immediate capture, otherwise reduce distance; avoid corners behind walls via clearance.
            val = (10**6 if (nx, ny) == (ox, oy) else 0) - (d * 100) + clearance(nx, ny)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), (ox, oy))
            val = d * 120 + clearance(nx, ny)
            # If capture is forced next step, avoid it if any alternative exists.
            if (nx, ny) == (ox, oy):
                val -= 10**7
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]