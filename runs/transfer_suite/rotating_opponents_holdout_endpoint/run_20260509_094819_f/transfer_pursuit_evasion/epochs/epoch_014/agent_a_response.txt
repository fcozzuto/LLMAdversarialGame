def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    self_evader = "evad" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score(nx, ny):
        d = cheb(nx, ny, ox, oy)
        if self_evader:
            # maximize distance; slightly prefer progressing toward far corners
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            prog = cheb(nx, ny, far_corner[0], far_corner[1]) * 0.01
            return d + prog
        else:
            # minimize distance to opponent; avoid pushing into corners behind walls not modeled -> small penalty for low mobility
            mobility = 0
            for dx, dy in moves:
                tx, ty = nx + dx, ny + dy
                if ok(tx, ty):
                    mobility += 1
            return -d + mobility * 0.02

    best = None
    best_mv = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score(nx, ny)
        if best is None or v > best:
            best = v
            best_mv = [dx, dy]
    return best_mv