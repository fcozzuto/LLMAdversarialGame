def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in moves:
            nx, ny = x + ddx, y + ddy
            if valid(nx, ny):
                c += 1
        return c

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        if i_am_pursuer:
            # minimize distance to evader; tie-break by mobility (more options)
            score = (-dist, mob, -nx, -ny)
        else:
            # evade: maximize distance; tie-break by mobility (avoid trapping)
            score = (dist, mob, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]