def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    if is_pursuer:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = d2(nx, ny, ox, oy)
                if best_val is None or v < best_val:
                    best_val = v
                    best_move = (dx, dy)
    else:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = d2(nx, ny, ox, oy)
                if best_val is None or v > best_val:
                    best_val = v
                    best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        dx, dy = 0, 0
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        dx, dy = 0, 0
    if not legal(sx + dx, sy + dy):
        for adx, ady in moves:
            if legal(sx + adx, sy + ady):
                return [int(adx), int(ady)]
        return [0, 0]
    return [int(dx), int(dy)]