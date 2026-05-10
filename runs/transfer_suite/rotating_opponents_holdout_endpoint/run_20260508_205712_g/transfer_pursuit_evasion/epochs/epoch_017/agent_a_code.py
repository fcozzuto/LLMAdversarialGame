def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    srole = str(observation.get("self_role", "")).lower()
    self_pursuer = ("purs" in srole) or ("chaser" in srole) or ("hunter" in srole) or ("pursuer" in srole)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy = 0, 0
    best_metric = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            metric = -10**9 if self_pursuer else 10**9
        else:
            # pursuer: minimize distance; evader: maximize distance
            d1 = cheb(nx, ny, ox, oy)
            d2 = man(nx, ny, ox, oy)
            metric = (d1 * 100 + d2)
            metric = -metric if self_pursuer else metric

        if best_metric is None or metric > best_metric:
            best_metric = metric
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]