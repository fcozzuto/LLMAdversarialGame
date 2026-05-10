def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if inside(x, y):
            obstacles.add((x, y))

    def parse_points(obj):
        pts = []
        for it in obj or []:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if inside(x, y):
                pts.append((x, y))
        return pts

    resources = parse_points(observation.get("resources", []))
    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in self_role for k in ("pursuer", "pursuit", "hunter", "chaser", "pursue"))

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx >= dy else dy

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)
        if target in obstacles:
            target = None

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if target is not None:
            dist_t = cheb(nx, ny, target[0], target[1])
            dist_o = cheb(nx, ny, ox, oy)
            score = 1000 - 20 * dist_t - (5 * dist_o if pursuer else -5 * dist_o)
        else:
            dist_o = cheb(nx, ny, ox, oy)
            score = dist_o if not pursuer else -dist_o
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]