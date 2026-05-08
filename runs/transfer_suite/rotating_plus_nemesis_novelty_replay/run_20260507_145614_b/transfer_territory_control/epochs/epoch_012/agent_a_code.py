def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        dx = nx - ox
        dy = ny - oy
        opp_dist = max(abs(dx), abs(dy))
        if resources:
            tx, ty = min(resources, key=lambda r: max(abs(r[0] - nx), abs(r[1] - ny)))
            dist = max(abs(tx - nx), abs(ty - ny))
            return (-dist) + 0.25 * opp_dist
        return 0.1 * opp_dist + (max(abs(nx - sx), abs(ny - sy)) == 0) * -0.05

    best = (0, 0)
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            sc = score_move(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
    return [int(best[0]), int(best[1])]