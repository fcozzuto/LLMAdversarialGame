def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    rset = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
                rset.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not res:
        # Avoid opponent if possible, else stay
        best = (0, 0)
        best_score = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = abs(nx - ox) + abs(ny - oy)
                if d > best_score or (d == best_score and (dx, dy) < best):
                    best_score, best = d, (dx, dy)
        return [best[0], best[1]]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_step = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Prefer stepping directly onto a resource
        cap_bonus = 10**6 if (nx, ny) in rset else 0

        # Score: minimize distance to nearest resource, maximize distance from opponent
        nd = min(dist((nx, ny), r) for r in res)
        od = dist((nx, ny), (ox, oy))
        score = cap_bonus - 1000 * nd + 3 * od

        if score > best_score or (score == best_score and (dx, dy) < best_step):
            best_score, best_step = score, (dx, dy)

    return [int(best_step[0]), int(best_step[1])]