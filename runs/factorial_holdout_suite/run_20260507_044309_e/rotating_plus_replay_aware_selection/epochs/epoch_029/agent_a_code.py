def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaking order already by list order.

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Evaluate candidate moves by best target they could capture (heuristic).
    best_move = (0, 0)
    best_score = -10**18
    center_x, center_y = w // 2, h // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer targets we reach earlier; then prefer closer, then prefer central.
            lead = do - ds  # positive => we reach earlier
            center = cheb(rx, ry, center_x, center_y)
            v = lead * 1000 - ds * 6 - center
            # Small deterministic bias to reduce dithering: prefer moving along gradient to that resource
            v += -abs((rx - nx)) - abs((ry - ny)) * 0.01
            if v > move_best:
                move_best = v

        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]