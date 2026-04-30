def choose_move(observation):
    x, y = observation["self_position"]
    oppx, oppy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((ox, oy) for ox, oy in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Target: closest resource; tie-break by lowest (y,x) then (x,y) for determinism
    best = None
    best_key = None
    for rx, ry in resources:
        d = man(x, y, rx, ry)
        key = (d, ry, rx)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dm = man(nx, ny, tx, ty)
            do = man(nx, ny, oppx, oppy)
            # Prefer approaching target, slightly prefer increasing distance from opponent
            score = (dm, -do, dy, dx, nx, ny)
            moves.append((score, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]