def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Strategy change: choose a "contested-safe" target by comparing approach distances.
    best_dxdy = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # If we'd move onto a resource, strongly prefer it.
        res_here = 1 if (nx, ny) in resources else 0
        # Compute maximum advantage over opponent among resources, weighted by closeness.
        # Higher: we reach sooner than opponent; lower: opponent reaches sooner.
        adv_best = -10**18
        if resources:
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # Prefer nearer resources overall and those where we are closer than opponent.
                val = (opd - myd) * 3 - (myd) + (1 if res_here and (rx, ry) == (nx, ny) else 0) * 100
                if val > adv_best:
                    adv_best = val
        else:
            adv_best = -dist(ox, oy, nx, ny)

        # Also avoid letting opponent immediately steal by moving too near their position.
        # (We aim to keep distance while still advancing to contested resources.)
        opp_prox_pen = dist(ox, oy, nx, ny)
        score = adv_best + res_here * 1000 - opp_prox_pen * 0.25

        # Deterministic tie-breaker: fixed ordering by preferring smaller |dx|+|dy| then lexicographic.
        tieb = - (abs(dx) + abs(dy)) * 0.01 - (0.001 * (dx + 1) + 0.0001 * (dy + 1))
        score += tieb

        if score > best_score:
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]