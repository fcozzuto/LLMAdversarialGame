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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dme = cheb(nx, ny, cx, cy)
            v = -dme - (dx == 0 and dy == 0) * 0.2
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose target deterministically: maximize race advantage first, then closeness, then tie-break by coords.
    best_t = resources[0]
    best_tv = -10**18
    for tx, ty in resources:
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        race = d_op - d_me
        v = race * 3.5 - d_me + (-(cheb(tx, ty, cx, cy)) * 0.05)
        if v > best_tv or (v == best_tv and (tx, ty) < best_t):
            best_tv = v
            best_t = (tx, ty)

    tx, ty = best_t

    # Pick move maximizing expected advantage for that target; also lightly prefer avoiding giving opponent a shorter path.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_me2 = cheb(nx, ny, tx, ty)
        d_op2 = cheb(ox, oy, tx, ty)
        race2 = d_op2 - d_me2
        v = race2 * 4.0 - d_me2
        # If we are not improving relative to staying, penalize a bit to reduce dithering.
        d_stay = cheb(sx, sy, tx, ty)
        if d_me2 >= d_stay:
            v -= 0.25
        # Tie-break by deterministic ordering favoring diagonals toward target.
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]