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

    best = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets where we have an edge; break ties by closer and then deterministic coords.
        val = (do - ds) * 1000000 + (0 - ds) * 10 + (rx - ry) * 0.001
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    target_dist = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_m = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; small bias to avoid oscillation: move that tends toward target in both axes.
        bias = abs((tx - nx)) * 0.0001 + abs((ty - ny)) * 0.0001
        score = (d, bias, dx, dy)
        if score < (best_m, 0, 0, 0) or (best_move == (0, 0) and d <= target_dist):
            pass
        if d < best_m:
            best_m = d
            best_move = (dx, dy)
        elif d == best_m:
            if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]