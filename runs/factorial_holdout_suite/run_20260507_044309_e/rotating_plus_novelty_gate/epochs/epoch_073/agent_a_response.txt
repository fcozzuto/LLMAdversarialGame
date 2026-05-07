def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    rset = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in rset:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2; a = -a if a < 0 else a
        b = y1 - y2; b = -b if b < 0 else b
        return a if a > b else b

    best = None
    best_score = -10**9
    # Target where I can arrive earlier than opponent; also prefer closer resources if tie.
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        s = (do - dme) * 100 + (-dme)  # win race first, then distance
        if s > best_score:
            best_score = s
            best = (rx, ry)

    # If no resources (shouldn't matter), drift toward opponent's corner to reduce time-to-block.
    if best is None:
        tx, ty = (w - 1, h - 1) if (sx + sy) % 2 == 0 else (0, 0)
    else:
        tx, ty = best

    # Choose move minimizing distance to target; deterministic tie-break favors toward increasing x then y then staying.
    def move_key(dx, dy, nx, ny):
        d = cheb(nx, ny, tx, ty)
        return (d, -dx, -dy, 0 if (dx == 0 and dy == 0) else 1)

    best_move = valid[0]
    best_key = move_key(best_move[0], best_move[1], best_move[2], best_move[3])
    for dx, dy, nx, ny in valid[1:]:
        k = move_key(dx, dy, nx, ny)
        if k < best_key:
            best_key = k
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]