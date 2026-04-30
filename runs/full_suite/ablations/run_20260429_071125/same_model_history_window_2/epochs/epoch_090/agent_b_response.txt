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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources, move toward opponent-side corner midpoint to avoid stagnation.
    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = (0, 0)
        bd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bd:
                bd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each possible move by the best "contested" target it heads toward.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer making progress to a resource that we're not hopelessly behind on.
        move_score = -10**18
        for tx, ty in resources:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Higher is better:
            # - closeness to target
            # - beating opponent (negative if opponent closer)
            # - prefer resources nearer the middle to keep flexibility
            mid_bias = 0.15 * cheb(tx, ty, w // 2, h // 2)
            s = (-1.2 * d_self) + (0.9 * (d_opp - d_self)) - mid_bias
            # Strong preference for immediate pickup/adjacent approach
            if d_self == 0:
                s += 1000
            elif d_self == 1:
                s += 25
            move_score = s if s > move_score else move_score

        # Small tie-break: reduce distance to opponent to reduce their ability to contest.
        tie = -0.05 * cheb(nx, ny, ox, oy)
        total = move_score + tie
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]