def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2 if abs(dx) == 1 and abs(dy) == 1 else 1
        return pen

    def best_target_score(x, y):
        if not resources:
            # fall back to blocking opponent direction
            return -cheb(x, y, ox, oy)
        # choose a resource where we're relatively closer than opponent
        best = -10**9
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer resources we can reach sooner and that are "swingy" vs opponent
            swing = do - ds
            # tie-break deterministically: nearer to center slightly
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = -abs(x - cx) - abs(y - cy)
            val = 6 * swing - ds + 0.1 * center
            if val > best:
                best = val
        return best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # evaluate each move; also discourage moving away from opponent when no resources
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = best_target_score(nx, ny)
        val -= obstacle_pen(nx, ny) * 3
        # keep some pressure: prefer decreasing distance to opponent when close contest
        if resources:
            val += 0.15 * (cheb(sx, sy, ox, oy) - cheb(nx, ny, ox, oy))
        else:
            val += 0.25 * (cheb(nx, ny, ox, oy) == 0)
            val += 0.1 * (-cheb(nx, ny, ox, oy))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]