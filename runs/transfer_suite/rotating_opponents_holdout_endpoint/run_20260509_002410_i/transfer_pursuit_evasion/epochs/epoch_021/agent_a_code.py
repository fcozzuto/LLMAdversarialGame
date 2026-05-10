def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    evader = ("evad" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in moves:
            tx, ty = x + ddx, y + ddy
            if legal(tx, ty):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1])) if evader else min(corners, key=lambda c: cheb(c[0], c[1]))
    cx, cy = far_corner

    best = None
    best_val = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny)
        m = mobility(nx, ny)
        corner_pull = cheb(nx, ny) - cheb(cx, cy)
        if evader:
            val = (d, m, corner_pull)
            if best is None or val > best_val:
                best, best_val = [ddx, ddy], val
        else:
            trap = m
            val = (-d, -trap, -corner_pull)
            if best is None or val > best_val:
                best, best_val = [ddx, ddy], val

    if best is None:
        return [0, 0]
    return best