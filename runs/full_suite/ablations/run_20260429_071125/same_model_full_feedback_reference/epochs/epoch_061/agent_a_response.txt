def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target: prefer resources we can reach earlier than opponent.
    best_target = None
    best_gain = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds  # positive means we are closer (or equal)
        key = (gain, -ds, rx, ry)
        if best_target is None or key > (best_gain, -cheb(sx, sy, best_target[0], best_target[1]), best_target[0], best_target[1]):
            best_target = (rx, ry)
            best_gain = gain

    if best_target is None:
        # No resources: drift away from opponent while staying obstacle-safe.
        tx, ty = (0, h - 1) if (sx + sy) < (ox + oy) else (w - 1, 0)
        best = None
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = cheb(nx, ny, tx, ty) + 0.5 * cheb(nx, ny, ox, oy)
            if val > best_val or (val == best_val and (nx, ny) < best):
                best_val = val
                best = (nx, ny)
        bx, by = best if best is not None else (sx, sy)
        return [bx - sx, by - sy]

    rx, ry = best_target

    # Move: maximize progress to target while avoiding opponent interference.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(nx, ny, ox, oy)
        # Strongly prefer reducing ds; also prefer keeping distance from opponent.
        score = (-10 * ds2) + (2 * do2) + (1 if (nx, ny) == (rx, ry) else 0)
        # Deterministic tie-break: smallest dx, then dy.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move