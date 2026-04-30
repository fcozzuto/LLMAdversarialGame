def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(ox, oy), (sx, sy)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target where we are closer than opponent; otherwise, disrupt by heading to shared "frontier"
    best_t = resources[0]
    best_val = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer being closer (negative), penalize long my distance, and slightly penalize letting opponent be too close
        val = (myd - opd) * 10 + myd + (1 if myd == 0 else 0) * 0.1
        if best_val is None or val < best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    cur_my = cheb(sx, sy, tx, ty)
    cur_op = cheb(ox, oy, tx, ty)

    # Move: minimize distance-to-target and maximize (or at least not reduce) opponent disadvantage; avoid getting too close to opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside_free(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        odist = cheb(nx, ny, ox, oy)
        # Deterministic tie-break uses score then lexicographic on move order
        score = (myd * 100) + (opd * 0) + (odist * -2)
        # also bias against moves that increase distance-to-target
        score += (1 if myd > cur_my else 0) * 50
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]