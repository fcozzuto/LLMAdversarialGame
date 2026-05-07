def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Score the move by how much it improves our advantage for the "most contestable" resource.
        best_for_move = -10**18
        best_close = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Our "net contest" for this resource: positive means we are closer than opponent.
            # Prefer resources where we are closer; if tied, prefer closer to take it next.
            net = do - ds
            # Small bonus for proximity to reduce dithering; stronger penalty when far behind.
            val = net * 1000 - ds
            if val > best_for_move or (val == best_for_move and ds < best_close):
                best_for_move = val
                best_close = ds

        # Tie-break: prioritize higher net advantage, then smaller best_close, then move order deterministically.
        key = (best_for_move, -best_close, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best