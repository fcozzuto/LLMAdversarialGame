def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we have reach advantage vs opponent (deterministic tie-break).
    best_r = resources[0]
    best_key = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher (do - ds) is better for us; then closer ds; then lexicographic.
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r

    # Evaluate one-step moves, avoid obstacle squares.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (d[0], d[1]))  # deterministic

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: reduce our distance; also try to increase opponent distance to target.
        ds1 = cheb(nx, ny, rx, ry)
        do1 = cheb(ox, oy, rx, ry)
        # Prefer moves that keep us from being immediately worse on distance; mild tie-break by board center.
        center_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)  # deterministic real
        score = (ds1, -do1, -center_bias, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves filtered (shouldn't), fallback.
    return [int(best_move[0]), int(best_move[1])]