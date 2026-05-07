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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Choose a target that I can reach soon, and break ties by how well I beat opponent.
        my_best = None
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            key = (d_my - d_op, d_my, rx, ry)
            if my_best is None or key < my_best:
                my_best = key
        # Prioritize immediate advantage; slight preference toward moving closer to that chosen resource.
        score = my_best[0] * 100 + (-my_best[1])
        # Deterministic tie-break on position.
        key2 = (score, -nx, -ny, dx, dy)
        if best is None or key2 > best:
            best = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]