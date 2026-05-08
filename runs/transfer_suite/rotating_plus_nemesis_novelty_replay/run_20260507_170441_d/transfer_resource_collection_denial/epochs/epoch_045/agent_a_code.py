def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = (None, None)  # (value, move)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Deny-oriented value: prefer states where we are closer than opponent to some resource.
        best_r = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Large when we beat opponent on that resource; small penalty for being far.
            val = (op_d - my_d) * 2 - my_d
            if best_r is None or val > best_r:
                best_r = val
        # Slight preference for staying mobile (avoid being stuck on edges), deterministic tie-break by dx,dy order.
        edge_pen = 0
        if nx == 0 or nx == w - 1:
            edge_pen += 0.1
        if ny == 0 or ny == h - 1:
            edge_pen += 0.1
        total = best_r - edge_pen
        if best[0] is None or total > best[0] or (total == best[0] and (dx, dy) < best[1]):
            best = (total, (dx, dy))

    return [best[1][0], best[1][1]]