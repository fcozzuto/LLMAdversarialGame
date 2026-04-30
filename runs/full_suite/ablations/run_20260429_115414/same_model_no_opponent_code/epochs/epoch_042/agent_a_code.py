def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no visible resources, drift toward the center to avoid wasting time.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    v = -mdist((nx, ny), (tx, ty))
                    if v > bestv:
                        bestv = v
                        best = (dx, dy)
        return [best[0], best[1]]

    my = (sx, sy)
    them = (ox, oy)

    # Choose a target resource: prefer those where we are closer than opponent.
    best_target = resources[0]
    best_t = -10**9
    for r in resources:
        d1 = mdist(my, r)
        d2 = mdist(them, r)
        # Higher is better: prioritize winning races; also prefer nearer.
        t = (d2 - d1) * 3 - d1
        if t > best_t:
            best_t = t
            best_target = r

    tx, ty = best_target

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        newp = (nx, ny)
        myd = mdist(newp, best_target)
        opd = mdist(them, best_target)

        # If we step onto a resource, it should dominate.
        on_res = 1 if best_target == (nx, ny) else 0

        # Slightly prefer moves that move toward the target while keeping opponent farther.
        val = on_res * 10**6 + (-myd) * 10 + (opd - myd) * 2

        # Micro-avoidance: don't take moves that increase distance to all resources too much.
        if resources:
            min_after = 10**9
            for r in resources:
                d = mdist(newp, r)
                if d < min_after:
                    min_after = d
            val += -min_after * 0.25

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]