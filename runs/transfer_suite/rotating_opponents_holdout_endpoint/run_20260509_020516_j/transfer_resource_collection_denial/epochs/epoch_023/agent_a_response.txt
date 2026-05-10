def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", None) or []
    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves2 = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves2.append((dx, dy, nx, ny))
    if not moves2:
        return [0, 0]

    if not resources:
        # Deterministic drift toward center while keeping away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves2:
            sc = -d((nx, ny), (cx, cy)) + 0.2 * d((nx, ny), (ox, oy))
            cand = (sc, -nx, -ny, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[3], best[4]]

    best = None
    for dx, dy, nx, ny in moves2:
        self_pos = (nx, ny)
        best_for_this = -10**9
        for p in resources:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) in obstacles:
                continue
            sd = d(self_pos, (rx, ry))
            od = d((ox, oy), (rx, ry))
            # Prefer being earlier than opponent; slight penalty for taking longer
            sc = (od - sd) - 0.08 * sd
            if sc > best_for_this:
                best_for_this = sc
        # Small secondary preference: closer to the best target and closer to center
        sc2 = best_for_this + 0.01 * (d((ox, oy), (sx, sy)) - d((nx, ny), (ox, oy))) - 0.001 * d(self_pos, ((w - 1) // 2, (h - 1) // 2))
        cand = (sc2, -d(self_pos, ((w - 1) // 2, (h - 1) // 2)), dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand
    return [int(best[2]), int(best[3])]