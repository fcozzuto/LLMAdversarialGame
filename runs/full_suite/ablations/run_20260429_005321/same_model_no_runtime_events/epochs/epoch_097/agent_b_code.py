def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [w - 1, h - 1]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        bestk = (-10**9, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            k = (-d, (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))
            if k > bestk:
                bestk, best = k, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = (-10**18, None)

    # Heuristic: pick a move that maximizes "net claim" on reachable resources,
    # with a small tie-break that also keeps distance from opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_d1 = (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy)

        # If we can grab a resource immediately, prioritize that strongly.
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in set(resources):
            cand = (10**9, -cheb(nx, ny, ox, oy), -move_d1)
            if cand > best_score:
                best_score, best_move = cand, (dx, dy)
            continue

        total = 0
        nearest_ours = 10**9
        nearest_theirs = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Claim value: prefer resources where we are closer by margin.
            adv = d2 - d1
            if adv > 0:
                v = 1000 + 40 * adv - 2 * d1
            else:
                # If we can't beat them, still consider blocking-less attractive but not zero.
                v = -50 - 3 * d1 - 10 * (-adv)
            total += v
            if d1 < nearest_ours: nearest_ours = d1
            if d2 < nearest_theirs: nearest_theirs = d2

        # Small opponent-avoidance / pressure: improve when we reduce their best access.
        pressure = (nearest_theirs - nearest_ours)
        cand = (total + 25 * pressure, -nearest_ours, -cheb(nx, ny, ox, oy), -move_d1)
        if cand > best_score:
            best_score, best_move = cand, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]