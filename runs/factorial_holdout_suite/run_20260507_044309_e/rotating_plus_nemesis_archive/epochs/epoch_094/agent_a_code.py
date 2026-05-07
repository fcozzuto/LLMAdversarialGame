def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti % 2 == 1:
        dirs = [d for d in dirs if d != (0, 0)] + [(0, 0)]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        move_score = -cheb(nx, ny, ox, oy) * 0.02  # slight stability
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            denom = ds + 1
            # Prefer resources we can reach no later than opponent, then closest.
            rel = do - ds
            s = 0
            if ds == 0:
                s += 1000
            if rel > 0:
                s += 120 * rel
            elif rel == 0:
                s += 40
            s += 20 / denom
            # Small tie-break to prefer nearer to opponent (deny lanes).
            s -= 0.1 * cheb(nx, ny, ox, oy)
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]