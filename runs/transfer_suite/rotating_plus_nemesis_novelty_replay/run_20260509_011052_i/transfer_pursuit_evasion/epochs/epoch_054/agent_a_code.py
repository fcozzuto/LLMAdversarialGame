def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    res = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    pursuer = True
    self_role = (observation.get("self_role") or "").lower()
    if "evader" in self_role:
        pursuer = False

    target = None
    if res:
        bestd = 10**9
        for r in res:
            rx, ry = r
            d = dist((sx, sy), (rx, ry))
            if d < bestd:
                bestd = d
                target = (rx, ry)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = 0
        if target is not None:
            s -= dist((nx, ny), target)
        dfo = dist((nx, ny), (ox, oy))
        if pursuer:
            s -= 0.5 * dfo
        else:
            s += 0.5 * dfo
        s += 0.01 * ((nx - sx) * 0 + (ny - sy) * 0)
        if s > best_score:
            best_score = s
            best_move = [dx, dy]
    return best_move