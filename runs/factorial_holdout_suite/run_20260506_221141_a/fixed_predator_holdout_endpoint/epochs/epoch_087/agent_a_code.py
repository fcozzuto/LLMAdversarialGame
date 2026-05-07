def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    best_val = None
    best_move = (0, 0)

    # Evaluate moves by "best resource after this move" and prefer arriving earlier than opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = do - ds  # positive means we are sooner
            # Strongly favor earlier arrival; if tied, favor closer-to-take and farther from us? (avoid)
            val = (ahead, -ds, -cheb(ox, oy, rx, ry))
            if local_best is None or val > local_best:
                local_best = val

        if local_best is None:
            continue
        # Prefer biggest ahead; if equal, prefer most immediate progress (smaller ds encoded by -ds).
        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    # Fallback: if something odd happens, attempt to move toward nearest legal resource.
    if best_move == (0, 0) and (sx, sy) not in obstacles:
        tgt = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        tx, ty = tgt
        mdx = 0 if tx == sx else (1 if tx > sx else -1)
        mdy = 0 if ty == sy else (1 if ty > sy else -1)
        for cand in [(mdx, mdy), (mdx, 0), (0, mdy), (0, 0)]:
            cx, cy = sx + cand[0], sy + cand[1]
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                return [int(cand[0]), int(cand[1])]

    return [int(best_move[0]), int(best_move[1])]