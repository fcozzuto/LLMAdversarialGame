def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy  # Chebyshev (diagonal allowed)

    best_score = None
    best_move = (0, 0)

    rr = resources  # local alias
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best resource "grab advantage" after this move.
        local_best = None
        for rx, ry in rr:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer grabbing before opponent; also prefer being closer if tie.
            # Slight bonus for nearer resources to encourage progress.
            sc = (do - ds, -ds, -abs(rx - nx) - abs(ry - ny))
            if local_best is None or sc > local_best:
                local_best = sc
        if local_best is None:
            continue
        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]