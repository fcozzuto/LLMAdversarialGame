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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Fallback: drift to a corner-biased target while avoiding obstacles.
    if not resources:
        tx = w - 1 if sx < w // 2 else 0
        ty = h - 1 if sy < h // 2 else 0
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            # keep distance from opponent a bit
            v += 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best else [0, 0]

    # Main: choose move that maximizes "winnable" proximity to some resource
    # where opponent is relatively farther; also avoid moves that are closer to obstacles via a light penalty.
    def obstacle_penalty(x, y):
        pen = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obstacles:
                    pen += 1
        return pen

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        op_dist = cheb(nx, ny, ox, oy)
        # Evaluate best target resource for this move
        v = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer smaller ds; prefer larger do (opponent farther)
            cand = (-1.2 * ds) + (0.75 * do) + (0.08 * op_dist) - (0.02 * ds * ds)
            if cand > v:
                v = cand
        v -= 0.05 * obstacle_penalty(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]