def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Precompute nearest resource distances for both agents
    def min_res_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    opp_near = min_res_dist(ox, oy)

    def obstacle_penalty(x, y):
        pen = 0
        for (bx, by) in obstacles:
            if abs(bx - x) <= 1 and abs(by - y) <= 1:
                pen += 4
        # Discourage stepping directly onto obstacles (should be blocked anyway by ok())
        if (x, y) in obstacles:
            pen += 100
        return pen

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    # Deterministic tie-break: score, then lexicographic dx,dy via dirs order above.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_near = min_res_dist(nx, ny)
        # Higher is better: being closer than opponent and closing the gap.
        gap = (opp_near - my_near)
        # Prefer improving our nearest distance; also mildly prefer moving (not required).
        score = gap * 100 - my_near * 2 - obstacle_penalty(nx, ny)
        # If we can reach a resource immediately, prioritize strongly.
        if any(cheb(nx, ny, rx, ry) == 0 for rx, ry in resources):
            score += 100000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]