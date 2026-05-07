def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for rx, ry in resources:
        dself = dist(sx, sy, rx, ry)
        dop = dist(ox, oy, rx, ry)
        # Prefer locations where we are closer than opponent; then closer overall; then lexicographic
        cand = (dself - dop, dself, rx, ry)
        if best is None or cand < best[0]:
            best = (cand, rx, ry)
    tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Minimize distance to target; discourage allowing opponent to get strictly closer
        ndself = dist(nx, ny, tx, ty)
        ndopp = dist(ox, oy, tx, ty)
        cand = (ndself, nx, ny, ndopp)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]