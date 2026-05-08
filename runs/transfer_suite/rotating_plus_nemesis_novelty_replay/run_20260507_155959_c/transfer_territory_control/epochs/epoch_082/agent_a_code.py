def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def free(x, y): 
        return inb(x, y) and (x, y) not in obstacles

    resources = observation.get("resources") or []
    t = None
    best = None
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                d = abs(x - sx) + abs(y - sy)
                if best is None or d < best or (d == best and (x, y) < t):
                    best = d
                    t = (x, y)

    target = t if t is not None else (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_val = None
    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # If chasing opponent, add slight preference for moving closer to opponent.
        val = -d
        if target == (ox, oy):
            val += -abs(nx - ox) - abs(ny - oy) * 0.01
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0) and not free(sx, sy):
        # Try any legal neighbor deterministically
        for dx, dy in moves[:-1]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
    return [best_move[0], best_move[1]]