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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    target = None
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat (opp closer => od - sd bigger), then closer to us
        score = (od - sd, -sd, -rx, -ry)
        if best is None or score > best:
            best = score
            target = (rx, ry)

    if target is None:
        # No visible resources: drift toward opponent's side deterministically
        tx = w - 1 if ox < w - 1 else 0
        ty = h - 1 if oy < h - 1 else 0
        target = (tx, ty)

    rx, ry = target
    step_dx = 0 if rx == sx else (1 if rx > sx else -1)
    step_dy = 0 if ry == sy else (1 if ry > sy else -1)

    def move_toward(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return None
        return (nx, ny)

    desired = move_toward(step_dx, step_dy)
    if desired is not None:
        return [step_dx, step_dy]

    # Blocked: pick among valid moves the one minimizing distance to target, then prefer overtaking opponent
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        key = (- (nod - nd), -nd, dx, dy)  # maximize (nd - nod) negativity? keep deterministic
        # Actually we want larger (nod - nd): "we beat them"; so minimize negative
        key = (-(nod - nd), nd, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]