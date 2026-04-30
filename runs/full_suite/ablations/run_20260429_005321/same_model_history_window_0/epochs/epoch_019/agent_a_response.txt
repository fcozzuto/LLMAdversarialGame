def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def step_towards(tx, ty):
        dx = tx - sx
        dy = ty - sy
        mdx = 0 if dx == 0 else (1 if dx > 0 else -1)
        mdy = 0 if dy == 0 else (1 if dy > 0 else -1)
        return [mdx, mdy]

    def cheb(ax, ay, bx, by):
        d1 = abs(ax - bx)
        d2 = abs(ay - by)
        return d1 if d1 > d2 else d2

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Material change: prioritize resources we are closer to than opponent (positive margin)
            # and prefer far-from-opponent when margins tie.
            margin = do - ds
            key = (margin, -do, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        rx, ry = best_r
        tx, ty = sx + step_towards(rx, ry)[0], sy + step_towards(rx, ry)[1]
        # Select among legal candidates the one that reduces our distance to target most,
        # with a small preference to increase distance from opponent.
        best_move = None
        best_val = None
        for dx, dy, nx, ny in candidates:
            v = (-cheb(nx, ny, rx, ry), cheb(nx, ny, ox, oy), -abs((nx + ny) - (rx + ry)))
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No resources: move to center while keeping away from opponent and obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = None
        best_val = None
        for dx, dy, nx, ny in candidates:
            v = (-cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), nx, ny)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]