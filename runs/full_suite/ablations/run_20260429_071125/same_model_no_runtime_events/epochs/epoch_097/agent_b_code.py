def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = w - 1, h - 1
        bestx = tx if tx != sx else sx
        besty = ty if ty != sy else sy
    else:
        best_score = None
        best_target = resources[0]
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets we can reach earlier; slightly prefer closer when tied.
            score = (do - ds, -ds, -(tx + ty))
            if best_score is None or score > best_score:
                best_score = score
                best_target = (tx, ty)
        bestx, besty = best_target

    # Greedy step toward target with deterministic obstacle-avoidance and small opponent-aware tie-break.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d1 = cheb(nx, ny, bestx, besty)
        d2 = cheb(ox, oy, bestx, besty)
        # If we can already reach the target at this step, prioritize it.
        reach_bonus = 1000 if (bestx == nx and besty == ny) else 0
        # Also prefer moves that don't give opponent a substantially better approach.
        opp_pen = cheb(nx, ny, ox, oy)
        cand.append((reach_bonus - d1 + (d2 - cheb(sx, sy, bestx, besty)) * 0.01 - opp_pen * 0.001, -dx, -dy, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][3]), int(cand[0][4])]