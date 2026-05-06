def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", None) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    resources = observation.get("resources", None) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def nearest_dist(px, py):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return (px - cx) ** 2 + (py - cy) ** 2
        best = None
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = nearest_dist(nx, ny)
        od = man(nx, ny, ox, oy)
        score = (sd, -od, dx, dy)  # primary: closer to resources/center; secondary: farther from opponent
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]