def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in legal:
        best_res = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer securing resources (ds small, do large), break ties by minimizing ds
            val = (do - ds, -ds)
            if best_res is None or val > best_res[0]:
                best_res = (val, rx, ry)
        # Small deterministic preference toward moves that reduce own distance to the best target
        (gap, negds), rx, ry = best_res
        self_after = -negds
        tie = (gap, -self_after, dx, dy)
        if best is None or tie > best[0]:
            best = (tie, dx, dy)

    return [best[1], best[2]]