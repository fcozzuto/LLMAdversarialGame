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

    # If we are a pursuer, go toward opponent; otherwise try to increase distance.
    towards = True
    if not self_is_pursuer and opp_is_pursuer:
        towards = False
    elif not self_is_pursuer and not opp_is_pursuer:
        towards = True
    elif self_is_pursuer and not opp_is_pursuer:
        towards = True

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        val = -d if towards else d
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        # Try staying put if valid; else pick any safe move deterministically.
        if inb(sx, sy) and not blocked(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]