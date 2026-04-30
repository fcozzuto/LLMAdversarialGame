def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in obstacles:
        return [0, 0]

    # If currently on an available resource, stay to secure.
    res_set = set(resources)
    if (sx, sy) in res_set:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Heuristic: pick move that minimizes our distance to a resource while maximizing distance advantage over opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer getting the resource first (sd < od), especially when close.
            lead = (od - sd)
            # Add a mild bias to closer resources overall.
            v = (lead * 100) - sd * 3 - cheb(nx, ny, 0, 0) * 0.01
            if v > move_val:
                move_val = v

        # Tie-breaker: deterministic preference for moves closer to opponent's side (usually centralized play).
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)
        elif move_val == best_val:
            if cheb(nx, ny, 0, 0) < cheb(sx + best_move[0], sy + best_move[1], 0, 0):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]