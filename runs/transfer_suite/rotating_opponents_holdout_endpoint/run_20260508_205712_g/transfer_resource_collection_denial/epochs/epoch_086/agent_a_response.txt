def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    # Evaluate each adjacent move by best contested resource score, with obstacle-aware filtering.
    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Small penalty for moving into "dead-ish" area (no valid neighbors).
        dead = 1
        cnt = 0
        for ddx, ddy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                cnt += 1
        if cnt > 0:
            dead = 0

        local_best = -10**18
        for rx, ry in res:
            myd = cheb((nx, ny), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            # Higher is better: win contested resources, then prioritize closer.
            # Bias slightly toward nearer resources to reduce wandering.
            val = (od - myd) * 100 - myd * 5 + (rx * 0.01 + ry * 0.001)
            if val > local_best:
                local_best = val

        # Prefer moves that keep up pressure; discourage being trapped.
        val_total = local_best - dead * 3
        if val_total > best_val or (val_total == best_val and (dx, dy) < best_move):
            best_val = val_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]