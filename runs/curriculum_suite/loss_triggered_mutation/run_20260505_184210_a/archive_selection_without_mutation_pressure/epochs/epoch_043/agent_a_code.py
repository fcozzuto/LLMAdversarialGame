def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    resources = observation.get("resources", []) or []
    rem = observation.get("remaining_resource_count", None)
    if rem is not None and rem <= 0:
        resources = []

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = man(rx, ry, sx, sy)
            do = man(rx, ry, ox, oy)
            key = (-do + ds, ds, rx, ry)  # closer to us, farther from opponent
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

        tx, ty = best
        best_move = None
        best_move_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ds2 = man(nx, ny, tx, ty)
            do2 = man(nx, ny, ox, oy)
            key = (ds2, -do2, dx, dy)
            if best_move_key is None or key < best_move_key:
                best_move_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = None
    best_move_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = man(nx, ny, cx, cy)
        do2 = man(nx, ny, ox, oy)
        key = (ds2, -do2, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]