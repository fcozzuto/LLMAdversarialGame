def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target by race advantage: prioritize resources where we are earlier or least behind.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # minimize ds; but strongly prefer (do - ds) (we want ds <= do)
        race = do - ds
        key = (race < 0, -race, ds, (rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose one-step move that best advances us to target while not stepping into obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If we are already closer/equal, maximize race improvement; otherwise, block by reducing opponent approach to target.
    want_adv = cheb(sx, sy, tx, ty) <= cheb(ox, oy, tx, ty)

    bestm = None
    bestmk = None
    for dx, dy, nx, ny in moves:
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # race_after = op_d - my_d ; maximize it => minimize negative
        race_after = op_d - my_d
        # tie-break by closeness
        key = (0 if want_adv else 1, -race_after, my_d, (nx, ny), dx, dy)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]