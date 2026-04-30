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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_for(posx, posy):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -king(posx, posy, ox, oy) - 0.1 * king(posx, posy, cx, cy)
        best = -10**9
        for tx, ty in resources:
            ds = king(posx, posy, tx, ty)
            do = king(ox, oy, tx, ty)
            # Prefer resources we can reach sooner than opponent; slight preference to closer resources overall
            v = (do - ds) * 10 - ds
            # Small bias toward moving away from opponent if similarly valued
            v += 0.1 * king(posx, posy, ox, oy)
            if v > best:
                best = v
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score_for(nx, ny)
        # Deterministic tie-break: prefer larger x then larger y, then smaller distance to center
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            bx, by = best_move
            nx2, ny2 = sx + bx, sy + by
            tie1 = (dx > bx) or (dx == bx and dy > by)
            tie2 = king(nx, ny, cx, cy) < king(nx2, ny2, cx, cy)
            if tie1 or (tie2 and not tie1):
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]