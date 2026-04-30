def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Choose a target where we are closer than the opponent (greedy "take advantage").
    best = None
    best_key = None
    for rx, ry in resources:
        selfd = dist2(sx, sy, rx, ry)
        oppd = dist2(ox, oy, rx, ry)
        key = (oppd - selfd, -selfd, rx, ry)  # maximize advantage, then closer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, head toward opponent corner to maintain pressure.
    if best is None:
        tx, ty = (w - 1, h - 1) if (sx <= w // 2 and sy <= h // 2) else (0, 0)
        bx, by = tx, ty
    else:
        bx, by = best

    # Evaluate each move by: get closer to target, and slightly deny opponent the same target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        selfd = dist2(nx, ny, bx, by)
        # Opponent denial: predict their next step approximately by best response toward target from their current pos.
        # (Simple: assume they move one step closer if possible, otherwise stay.)
        o_best = dist2(ox, oy, bx, by)
        for odx, ody in moves:
            mx, my = ox + odx, oy + ody
            if ok(mx, my):
                o_best = min(o_best, dist2(mx, my, bx, by))
        oppd = o_best
        val = (-selfd, oppd, abs(nx - ox) + abs(ny - oy), -((dx == 0 and dy == 0) * 1))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]