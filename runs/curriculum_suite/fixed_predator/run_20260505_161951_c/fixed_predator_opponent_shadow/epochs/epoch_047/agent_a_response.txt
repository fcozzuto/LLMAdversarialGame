def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, tx, ty)
            key = (d, man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
                ans = (dx, dy)
        return [ans[0], ans[1]]

    best_key = None
    best_move = (0, 0)

    # Deterministic ordering to break ties consistently
    resources_sorted = sorted(resources)

    for dx, dy, nx, ny in moves:
        # Prefer closer to resources, but deny opponent by favoring cells where we are no farther than them
        # and where opponent would need extra time to reach our intended resource.
        best_cell_key = None
        for rx, ry in resources_sorted:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # If opponent is already closer, attempt an "intercept" by using a midpoint toward that resource.
            if do <= ds:
                mx, my = (rx + ox) // 2, (ry + oy) // 2
                di = man(nx, ny, mx, my)
                target_score = (1, di, ds)  # higher priority: contest by moving toward intercept region
            else:
                # We can win the resource; prioritize reducing our distance and increasing opponent delay
                target_score = (0, ds, (do - ds), man(nx, ny, ox, oy))
            # Collect the best resource-contest plan for this move
            key = target_score
            if best_cell_key is None or key < best_cell_key:
                best_cell_key = key

        # Global objective: minimize distance-based key; add slight penalty for moving away from center line to avoid tail chasing
        center_pen = man(nx, ny, (ox + sx) // 2, (oy + sy) // 2)
        global_key = (best_cell_key, center_pen, dx, dy)
        if best_key is None or global_key < best_key:
            best_key = global_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]