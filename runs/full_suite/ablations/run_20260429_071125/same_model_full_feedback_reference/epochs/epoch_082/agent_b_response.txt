def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # If no resources, move toward center deterministically to stay flexible.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestm = -10**18, (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = -cheb(nx, ny, cx, cy)
            if score > best:
                best, bestm = score, (dx, dy)
        return [bestm[0], bestm[1]]

    # Precompute opponent nearest distance per resource for deterministic comparison.
    opp_d = []
    for rx, ry in resources:
        opp_d.append((cheb(ox, oy, rx, ry), (rx, ry)))

    # Candidate move scoring: prioritize resources where we can be strictly closer than opponent,
    # with secondary preference for reducing our own distance and avoiding edge stagnation.
    best, bestm = -10**18, (0, 0)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_local = -10**18
        for od, (rx, ry) in opp_d:
            md = cheb(nx, ny, rx, ry)
            # If we can arrive sooner than opponent, it dominates.
            lead = od - md
            val = lead * 100 - md * 2
            if val > best_local:
                best_local = val

        # Encourage progress toward a promising resource without getting too far from the board center.
        center_pen = cheb(nx, ny, cx, cy)
        score = best_local - center_pen * 0.1

        if score > best:
            best, bestm = score, (dx, dy)

    return [bestm[0], bestm[1]]