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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def score_move(nx, ny):
        d = dist2(nx, ny, ox, oy)
        if is_evader:
            # maximize distance, but avoid corners/obstacles by preferring higher mobility
            mobility = 0
            for ax, ay in deltas:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and not blocked(tx, ty):
                    mobility += 1
            corner_pen = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
            return d * 10 - corner_pen * 3 + mobility
        else:
            # pursuer: minimize distance; slight tie-break toward higher mobility
            mobility = 0
            for ax, ay in deltas:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and not blocked(tx, ty):
                    mobility += 1
            return -d * 10 + mobility

    best_dx, best_dy = 0, 0
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sc = score_move(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]