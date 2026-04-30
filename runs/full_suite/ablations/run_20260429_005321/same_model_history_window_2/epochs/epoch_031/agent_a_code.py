def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    best = None
    best_val = None
    for p in resources:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obst:
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer larger advantage over opponent; break ties by smaller self distance
                val = (do - ds, -ds)
                if best is None or val > best_val:
                    best = (rx, ry)
                    best_val = val

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if best is not None:
        tx, ty = best
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # move that reduces our distance to target; also keep advantage if possible
            score = (-ds, -(do - ds))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return [best_move[0], best_move[1]]

    # No resources: move toward center, keeping deterministic tie-breakers
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, cx, cy)
        # Prefer smaller distance; avoid getting closer to opponent slightly
        oppd = cheb(nx, ny, ox, oy)
        score = (-dist, oppd)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [best_move[0], best_move[1]]