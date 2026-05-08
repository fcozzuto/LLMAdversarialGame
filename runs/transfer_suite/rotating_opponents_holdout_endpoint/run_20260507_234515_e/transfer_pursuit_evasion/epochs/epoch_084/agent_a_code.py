def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursue" in role)
    best = None
    best_move = [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)
        if is_pursuer:
            val = (-dist, -abs(nx - ox) - abs(ny - oy))  # minimize Chebyshev first
        else:
            val = (dist, abs(nx - ox) + abs(ny - oy))   # maximize Chebyshev first
        # deterministic tie-break: lexicographic on move
        if best is None or val > best or (val == best and [dx, dy] < best_move):
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]