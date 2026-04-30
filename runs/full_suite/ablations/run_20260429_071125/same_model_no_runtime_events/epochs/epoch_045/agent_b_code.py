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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (matches 8-direction move costs)

    best_target = None
    best_val = -10**18

    for rx, ry in resources:
        ds = kdist(sx, sy, rx, ry)
        do = kdist(ox, oy, rx, ry)
        val = (do - ds) * 1000 - ds  # prioritize resources we reach sooner
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = best_target

    # Choose move that decreases distance to target; break ties to keep away from opponent.
    best_move = [0, 0]
    best_mscore = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dnow = kdist(nx, ny, tx, ty)
        dprev = kdist(sx, sy, tx, ty)
        do_now = kdist(nx, ny, ox, oy)
        do_prev = kdist(sx, sy, ox, oy)
        mscore = (dprev - dnow) * 1000 - dnow + (do_now - do_prev) * 2
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]