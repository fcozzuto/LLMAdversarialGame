def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic fallback: head to opposite corner quadrant
        tx, ty = (w - 1, h - 1) if (sx < w // 2) else (0, h - 1 if sy < h // 2 else 0)

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # choose the most "contested" resource for our step by maximizing advantage
            step_score = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # prefer immediate/near grabs and deny opponent; add small bias to reduce own distance to all
                sc = (opd - myd) * 100 - myd * 3 + (1 if myd == 0 else 0) * 1000 - (1 if opd == 0 else 0) * 500
                if sc > step_score:
                    step_score = sc
        else:
            myd = cheb(nx, ny, tx, ty)
            step_score = -myd

        # slight bias to progress generally toward best resource direction deterministically:
        # prefer moves that reduce distance to nearest resource from current state (ties broken by move order)
        if resources:
            cur_best = 10**9
            nxt_best = 10**9
            for rx, ry in resources:
                cur_best = min(cur_best, cheb(sx, sy, rx, ry))
                nxt_best = min(nxt_best, cheb(nx, ny, rx, ry))
            step_score += (cur_best - nxt_best) * 5

        if step_score > best_score:
            best_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]