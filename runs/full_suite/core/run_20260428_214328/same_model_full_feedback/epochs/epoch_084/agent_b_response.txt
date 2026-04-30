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
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            score = 0
            # Pick the single best target by "race advantage"
            best_t = None
            best_t_val = -10**18
            for tx, ty in resources:
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                # Prefer targets I can reach earlier than opponent
                val = (opd - myd) * 100 - myd * 3 + cheb(tx, ty, cx, cy) * -1
                if val > best_t_val:
                    best_t_val = val
                    best_t = (tx, ty, myd, opd)
            if best_t:
                tx, ty, myd, opd = best_t
                score = best_t_val + (opd - myd) * 10
            # Small preference for moving toward center when values tie
            score += -cheb(nx, ny, cx, cy) * 0.1
        else:
            score = -cheb(nx, ny, cx, cy)

        # Deterministic tie-breaker: lower my distance to center, then lexicographic dx/dy
        tie_key = (score, -cheb(nx, ny, cx, cy), -dx, -dy)
        best_key = (best_score, -cheb(sx + best_move[0], sy + best_move[1], cx, cy), -best_move[0], -best_move[1])
        if tie_key > best_key:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]