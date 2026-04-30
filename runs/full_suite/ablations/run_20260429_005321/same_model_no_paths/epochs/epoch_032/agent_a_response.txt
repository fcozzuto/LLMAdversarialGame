def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            v = -d
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Deterministic choice: maximize "pressure" margin (opponent farther than self), plus mild tie-break toward nearest.
    best_move = (0, 0)
    best_val = -10**18
    # Fixed iteration order already deterministic; compute for each possible next move.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = -10**18
        # Choose best target for this move (also deterministic).
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets where we are closer than opponent; also reduce our distance.
            pressure = (do - ds)
            # Small deterministic tie-break: prefer lexicographically smaller targets to stabilize.
            dist_pen = ds * 0.01
            tx_bias = (tx * 0.000001) + (ty * 0.0000001)
            v = pressure - dist_pen - tx_bias
            if v > val:
                val = v
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]