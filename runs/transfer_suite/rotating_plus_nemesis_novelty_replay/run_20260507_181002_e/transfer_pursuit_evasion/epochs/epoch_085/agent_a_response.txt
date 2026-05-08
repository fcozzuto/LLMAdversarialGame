def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "")
    is_evader = ("evad" in role.lower())

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        adb = adj_block(nx, ny)
        edge = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        edge_pen = 0 if edge >= 2 else (2 - edge) * 0.6
        if is_evader:
            score = d + 0.35 * edge - 1.1 * adb - edge_pen
        else:
            score = -d + 0.35 * edge - 1.1 * adb - edge_pen
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]