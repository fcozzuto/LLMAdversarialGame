def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    deltas = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    best = (10**9, 10**9, 10**9)  # (dist, -progress, tie)
    best_move = [0, 0]

    start_d = cheb(sx, sy, int(tx), int(ty))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, int(tx), int(ty))
        progress = start_d - d
        # deterministic tie-break: prefer diagonal, then x direction, then y direction via tuple order
        tie = abs(nx - cx) + abs(ny - cy)
        cand = (d, -progress, tie)
        if cand < best:
            best = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]