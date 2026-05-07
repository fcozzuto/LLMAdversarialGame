def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best = (0, 0)
    best_val = None
    near_opp_pen = 1.0 / 8.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        move_val = -10**9
        for rx, ry in res:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            if self_d == 0:
                val = 10**6 + (opp_d * 0.01)
            else:
                advantage = (opp_d - self_d)
                val = advantage * 100 - self_d * 2
            # discourage stepping into opponent neighborhood (capture races)
            od = dist(nx, ny, ox, oy)
            if od <= 1:
                val -= (2 - od) * 20
            val -= (abs(rx - nx) + abs(ry - ny)) * near_opp_pen
            if val > move_val:
                move_val = val
        if best_val is None or move_val > best_val:
            best_val = move_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]