def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    danger = (cheb(sx, sy, ox, oy) <= 2)
    best_score = -10**18
    best_move = [0, 0]

    # If no visible resources, drift to the corner opposite the opponent.
    if not resources:
        target = (0 if ox > w // 2 else w - 1, 0 if oy > h // 2 else h - 1)
        resources = [target]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose target that is best for us AND least attractive to the opponent (deny).
        local_best = -10**18
        for rx, ry in resources:
            d_us = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)
            # Higher is better: closer to resource, farther from opponent.
            s = (-d_us) + (0.9 * d_opp)
            local_best = s if s > local_best else local_best

        # If we're close to opponent, prioritize increasing distance.
        dist_now = cheb(nx, ny, ox, oy)
        score = local_best + (5.0 * dist_now if danger else 1.5 * dist_now)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move