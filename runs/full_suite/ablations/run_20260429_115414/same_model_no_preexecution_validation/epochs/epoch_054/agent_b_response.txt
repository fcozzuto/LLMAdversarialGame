def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target by maximizing (opp_dist - my_dist); break ties by smaller my_dist then stable order.
    best = None
    for tx, ty in resources:
        dm = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - dm
        key = (adv, -dm, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty), dm, do)
    (_, (tx, ty), dm, do) = best

    # If we're not ahead, try to make a material change: go to a cell that increases our advantage margin.
    # Otherwise, go directly to target.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (-(10**18), [0, 0])
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dm2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        margin = do2 - dm2
        # Tie-break: closer to target slightly, avoid staying unless best.
        score = margin * 1000 + (do2 - dm2) + (-dm2) + (-1 if (dx == 0 and dy == 0) else 0)
        # Also slightly prefer staying within the board quadrant toward the target.
        score += -abs(nx - tx) - abs(ny - ty)
        if score > best_move[0]:
            best_move = (score, [dx, dy])

    return best_move[1]