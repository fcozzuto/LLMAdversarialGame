def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    pursuer_mode = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_score(nx, ny):
        d = cheb(nx, ny, ox, oy)
        if pursuer_mode:
            return -d  # minimize distance
        else:
            return d   # maximize distance

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        v = best_score(nx, ny)
        if best is None or v > best_val:
            best = (dx, dy)
            best_val = v
        elif v == best_val and best is not None:
            # deterministic tie-break: prefer moving toward/away along x then y, then diagonals, then stay
            def key(m):
                mx, my = m
                return (mx == 0, my == 0, mx != 0 and my != 0, mx == 0 and my == 0)
            if key((dx, dy)) < key(best):
                best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]