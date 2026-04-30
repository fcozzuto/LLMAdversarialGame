def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def sign(z): return 0 if z == 0 else (1 if z > 0 else -1)
    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    best = -10**18
    if resources:
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do < INF:  # placeholder removed below
                pass
            score = (do - ds) * 10 - ds
            if score > best:
                best = score
                target = (rx, ry)

    if target is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(tx + 0.5), int(ty + 0.5))

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer reaching target sooner, but also consider opponent's relative advantage.
        val = (do2 - ds2) * 10 - ds2
        # Deterministic tie-break: prefer lexicographically smaller move delta after val.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]