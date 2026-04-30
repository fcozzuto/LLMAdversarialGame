def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_penalty(x, y):
        # discourage moving adjacent to obstacles to avoid getting stuck
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_dx, best_dy = 0, 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # choose resource where we are relatively closer than opponent
            best_local = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                rel = do - ds  # positive means we can reach earlier
                # also prefer generally closer resources
                score = rel * 10 - ds - 0.5 * obstacle_penalty(nx, ny)
                if score > best_local:
                    best_local = score
            cand = best_local
        else:
            # no resources visible: go toward center while keeping distance from opponent
            dcent = cheb(nx, ny, int(cx), int(cy))
            dopp = cheb(nx, ny, ox, oy)
            cand = dopp * 2 - dcent - 0.5 * obstacle_penalty(nx, ny)

        # deterministic tie-break: prefer staying if equal, then lower |dx| then lower |dy|, then lexicographic
        if best is None or cand > best:
            best = cand
            best_dx, best_dy = dx, dy
        elif cand == best:
            if (dx == 0 and dy == 0) and not (best_dx == 0 and best_dy == 0):
                best_dx, best_dy = dx, dy
            else:
                if (abs(dx), abs(dy), dx, dy) < (abs(best_dx), abs(best_dy), best_dx, best_dy):
                    best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]