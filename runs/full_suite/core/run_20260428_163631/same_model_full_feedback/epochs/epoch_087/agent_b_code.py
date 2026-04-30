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
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose best resource by (we are closer than opponent) and closeness.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning the race; also break ties deterministically.
        score = (do - ds) * 1000 - ds
        score += (rx * 11 + ry * 7) * 1e-6
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # No resources; move to increase distance from opponent.
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_score:
                best_score = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best
    # Try step that decreases our distance; avoid getting worse relative to opponent.
    ordered = sorted(dirs, key=lambda d: (cheb(sx + d[0], sy + d[1], tx, ty), d[0], d[1]))
    best_move = (0, 0)
    best_score = -10**18
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        # If opponent can reach much sooner, prefer safer moves.
        rel = (cur_do - ns) - (cur_do - cur_ds)  # how our race advantage changes (approx)
        score = (cur_do - ns) * 1000 - ns + rel * 10
        # Slightly prefer staying on improving gradient towards target.
        score += -(abs(nx - tx) + abs(ny - ty)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]