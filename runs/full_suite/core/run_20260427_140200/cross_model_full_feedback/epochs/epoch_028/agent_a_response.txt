def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_opp = dist(nx, ny, ox, oy)
        score = 0.25 * d_opp

        if resources:
            # closest resource drives movement; slight preference for moves that reduce distance
            closest = None
            bestd = None
            for rx, ry in resources:
                dd = dist(nx, ny, rx, ry)
                if bestd is None or dd < bestd:
                    bestd = dd
                    closest = (rx, ry)
            if closest is not None:
                crx, cry = closest
                cur_before = dist(sx, sy, crx, cry)
                after = dist(nx, ny, crx, cry)
                score += 5.0 * (1.0 if (nx, ny) == (crx, cry) else 0.0)
                score += 2.0 * (cur_before - after)
                score += -1.5 * after

        # deterministic tie-break: prefer smaller dx, then dy, then higher score
        cand = (score, -dx, -dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]