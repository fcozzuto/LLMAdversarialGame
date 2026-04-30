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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    if resources:
        best = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources where we are closer than opponent; avoid where opponent is significantly closer.
            # Also break ties deterministically by coordinates.
            score = (do - ds) * 100 - ds * 2
            key = (score, -tx, -ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        target = best[1]
    else:
        # No visible resources: move toward opponent side while keeping distance from obstacles.
        tx, ty = (w - 1 if sx < w // 2 else 0), (h - 1 if sy < h // 2 else 0)
        target = (tx, ty)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)

        # Obstacle-adjacent penalty encourages safer paths without full search.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_pen += 3

        # If we can get onto/near the target earlier than opponent, prioritize; otherwise maintain distance from opponent.
        opp_dist = cheb(nx, ny, ox, oy)
        val = (d_opp - d_self) * 80 - d_self * 3 + opp_dist - adj_pen
        key = (val, -nx, -ny)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]