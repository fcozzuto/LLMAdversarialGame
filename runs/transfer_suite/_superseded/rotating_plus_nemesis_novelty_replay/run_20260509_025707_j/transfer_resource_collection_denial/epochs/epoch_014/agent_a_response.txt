def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    res_set = set((r[0], r[1]) for r in resources)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Primary: maximize our advantage over opponent on the best remaining resource.
        # Secondary: prefer immediate pickup and reducing distance to nearest contested resource.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                od = md(ox, oy, rx, ry)
                local_best = max(local_best, 10**9 - od)
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Advantage: positive if we are closer than opponent; prioritize winning races.
            adv = od - sd
            # Tie-breaker: shorter combined distance (both go there quickly).
            tight = -(sd + od)
            val = adv * 1000 + tight
            if val > local_best:
                local_best = val

        # Add mild anti-cling to avoid standing still when tied.
        if (dx, dy) == (0, 0):
            local_best -= 3

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]