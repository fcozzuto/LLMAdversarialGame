def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we have distance advantage over the opponent.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Large weight for advantage, then shorter self distance, then deterministic tie-break.
        score = (do - ds) * 1000000 - ds * 10 - rx - ry * 0.001
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Move toward target with simple obstacle-aware tie-breaking by best resulting score.
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**15
        # Prefer reducing distance to target; also avoid letting opponent get strictly closer.
        dsn = cheb(nx, ny, tx, ty)
        don = cheb(ox, oy, tx, ty)
        adv = don - dsn
        # Secondary: prefer staying within grid already ensured; deterministic by coords.
        return adv * 1000000 - dsn * 10 - nx - ny * 0.001

    best_d = (0, 0)
    best_ms = -10**15
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            ms = move_score(nx, ny)
            if ms > best_ms:
                best_ms = ms
                best_d = (dx, dy)

    return [int(best_d[0]), int(best_d[1])]