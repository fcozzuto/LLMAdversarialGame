def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If there are resources, move toward the closest one, preferring moves that bring us closer
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Heuristic: prioritize reducing distance to resource and keeping safe distance from opponent
            score = -d_me * 2 + d_opp
            # Evaluate move llegar
            for dx, dy, nx, ny in legal:
                nd = dist((nx, ny), (rx, ry))
                danger = abs(nx - ox) + abs(ny - oy)
                sc = -nd * 2 + danger
                if best_score is None or sc > best_score:
                    best_score = sc
                    best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    # Fallback: move away from opponent if possible, else toward center
    best = None
    best_score = None
    center = (w // 2, h // 2)
    for dx, dy, nx, ny in legal:
        # prefer increasing distance from opponent
        d_opp_before = dist((sx, sy), (ox, oy))
        d_opp_after = dist((nx, ny), (ox, oy))
        score = (d_opp_after - d_opp_before)  # want positive (increase distance)
        # tie-breaker: closer to center
        score2 = -dist((nx, ny), center)
        sc = score * 2 + score2
        if best_score is None or sc > best_score:
            best_score = sc
            best = (dx, dy)
    if best is not None:
        return [int(best[0]), int(best[1])]

    return [0, 0]