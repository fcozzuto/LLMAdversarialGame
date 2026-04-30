def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    if not resources:
        # Default: move toward board center
        tx, ty = w // 2, h // 2
        best = None
        bestd = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (nx, ny) < best):
                bestd = d
                best = (nx, ny)
        nx, ny = best
        return [nx - sx, ny - sy]

    # Choose a target where our relative distance is best (smaller gap = we are closer than opponent)
    best_target = None
    best_key = None  # (gap, self_dist, target_x, target_y)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gap = ds - do
        key = (gap, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Pick move minimizing our distance to target; break ties by improving relative gap after move
    best_move = None
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        gap = ns - no
        score = (ns, gap, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]