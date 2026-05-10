def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    pref = (0, 0)
    path = observation.get("self_path") or []
    if len(path) >= 2:
        x0, y0 = path[-2]
        x1, y1 = path[-1]
        dx, dy = x1 - x0, y1 - y0
        pref = (0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            return -10**9
        s = 0
        if resources:
            rx, ry = resources[0]
            s -= abs(rx - nx) + abs(ry - ny)
        s -= 0.2 * (abs(ox - nx) + abs(oy - ny))  # slight pressure
        if (dx, dy) == pref:
            s += 1
        return s

    best = None
    best_s = -10**9
    for dx, dy in dirs:
        s = score_move(dx, dy)
        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]