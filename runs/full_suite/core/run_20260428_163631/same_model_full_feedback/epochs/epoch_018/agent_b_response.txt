def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_set = set(resources)

    # If we can pick now, do it deterministically (best advantage).
    best_pick = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny) and (nx, ny) in res_set:
            myd = cd(nx, ny, nx, ny)
            opd = cd(ox, oy, nx, ny)
            adv = opd - myd
            key = (adv, -cd(ox, oy, nx, ny), nx, ny)
            if best_pick is None or key > best_pick[0]:
                best_pick = (key, [dx, dy])
    if best_pick is not None:
        return best_pick[1]

    # Choose a target resource where we are relatively ahead vs opponent.
    if resources:
        best = None
        for rx, ry in resources:
            myd = cd(sx, sy, rx, ry)
            opd = cd(ox, oy, rx, ry)
            # Prefer reachable sooner; also deny opponent.
            score = (opd - myd) * 100 - myd + (1 if myd == 0 else 0)
            tie = (-opd, rx, ry)
            key = (score, tie)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    # Pick the move that minimizes our distance to target; if tied, improves advantage and avoids dead-ends.
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        myd = cd(nx, ny, tx, ty)
        opd = cd(ox, oy, tx, ty)
        adv = opd - myd
        # Prefer moves that reduce our distance and keep options (local safety).
        options = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if safe(ax, ay):
                options += 1
        key = (-myd, adv, options, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move