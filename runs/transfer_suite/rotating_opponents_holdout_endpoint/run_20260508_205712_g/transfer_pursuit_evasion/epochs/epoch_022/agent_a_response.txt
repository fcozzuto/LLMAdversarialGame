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
    pursuer = ("pursuer" in srole) or ("chaser" in srole) or ("pursue" in srole)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def adj_block_pen(x, y):
        pen = 0
        for dx, dy in moves:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d = abs(x - cx) + abs(y - cy)
        return d

    best = None
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        block_pen = adj_block_pen(nx, ny)
        cpen = center_bias(nx, ny)

        # Deterministic scoring:
        # Pursuer: minimize distance; penalize being near obstacles.
        # Evader: maximize distance; prefer center to avoid corner/edge traps; penalize obstacle adjacency.
        if pursuer:
            val = d * 10 + block_pen * 2 + cpen * 0.01
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < tuple(best_move))
        else:
            val = -d * 10 + block_pen * 2 - cpen * 0.05  # center preferred => lower penalty
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < tuple(best_move))

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move