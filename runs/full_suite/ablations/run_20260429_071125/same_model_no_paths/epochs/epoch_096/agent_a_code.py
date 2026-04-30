def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources: move to maximize separation from opponent, prefer toward center
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sep = cheb(nx, ny, ox, oy)
            cen = -cheb(nx, ny, cx, cy)
            v = sep * 5 + cen
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18

    # Deterministic ordering tie-break by (dx,dy) lexicographic
    dirs_sorted = sorted(dirs)

    for dx, dy in dirs_sorted:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Base: keep distance from opponent (approximate)
        sep = cheb(nx, ny, ox, oy)

        # Target: resource that best advances us while being worst for opponent
        min_self = 10**9
        best_for_us = 10**9
        best_adv = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = (d_opp - d_self)  # higher means we are closer than opponent to that resource
            if adv > best_adv:
                best_adv = adv
                best_for_us = d_self
            if d_self < min_self:
                min_self = d_self

        # Combine: strongly prefer getting closer to resources and securing advantage over opponent
        # Also add small penalty if not improving toward the nearest resource.
        v = best_adv * 12 - min_self * 3 + sep * 1
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]