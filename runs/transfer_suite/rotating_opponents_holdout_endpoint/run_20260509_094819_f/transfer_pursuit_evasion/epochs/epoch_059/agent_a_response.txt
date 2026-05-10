def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "").lower()
    i_am_pursuer = ("purs" in role) or ("catch" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        # One-step deterministic lookahead to break ties against zigzags
        if i_am_pursuer:
            # Prefer smaller distance; penalize moves that increase distance in next step
            next_best = 10**9
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if not legal(tx, ty):
                    tx, ty = nx, ny
                nd = cheb(tx, ty, ox, oy)
                if nd < next_best:
                    next_best = nd
            val = (-next_best * 1000) - d
        else:
            # Prefer larger distance; penalize moves that reduce distance quickly
            next_best = -10**9
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if not legal(tx, ty):
                    tx, ty = nx, ny
                nd = cheb(tx, ty, ox, oy)
                if nd > next_best:
                    next_best = nd
            val = (next_best * 1000) + d

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]