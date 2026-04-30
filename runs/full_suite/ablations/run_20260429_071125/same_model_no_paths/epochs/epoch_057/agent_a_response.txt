def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource that we can claim earlier than the opponent.
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        dself = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Higher is better: prioritize winning a resource, then closeness.
        lead = dop - dself
        score = (lead * 100) - dself - 0.15 * dop
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    # If no resources, go toward center/escape obstacles.
    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    # Choose move that reduces distance to target while not worsening opponent too much.
    best_m = [0, 0]
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        # If opponent is also near the target, slightly favor positions that keep distance.
        dop = cheb(ox, oy, tx, ty)
        # Also encourage getting closer to any resource if target isn't available.
        min_other = 0
        if resources:
            best = 10**9
            for rx, ry in resources:
                best = min(best, cheb(nx, ny, rx, ry))
            min_other = best
        v = (-dself * 10) + (-0.6 * dop) + (-0.35 * min_other)
        # Small tie-break: move toward target's quadrant.
        v += -0.01 * (abs(nx - tx) + abs(ny - ty))
        if v > best_v:
            best_v = v
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]