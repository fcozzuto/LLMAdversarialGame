def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target we can reach with a distance advantage.
    best_t = resources[0]
    best_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer big advantage; tie-break by nearer and then by coordinates.
        score = (do - ds, -ds, tx, ty)
        if best_score is None or score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Main objective: decrease distance to target.
        d_new = cheb(nx, ny, tx, ty)
        d_cur = cheb(sx, sy, tx, ty)

        # Secondary: block opponent by moving toward resources where we get/keep advantage.
        opp_adv = cheb(ox, oy, tx, ty) - d_new

        # Obstacle proximity penalty (stay away if possible).
        if obstacles:
            mind = 10**9
            for ax, ay in obstacles:
                d = cheb(nx, ny, ax, ay)
                if d < mind: mind = d
            obst_pen = 0 if mind >= 2 else (3 - mind) * 2
        else:
            obst_pen = 0

        val = (opp_adv, -(d_new), -(d_new - d_cur), -obst_pen, -abs(nx - ox) - abs(ny - oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]