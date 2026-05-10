def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def free_degree(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("pursuer" in role)

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        deg = free_degree(nx, ny)
        edge = (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
        # Deterministic tie-break: fixed ordering of moves.
        if is_pursuer:
            val = (-man, -deg, -int(edge), 0)
        else:
            val = (man, -deg, -int(edge), 0)
        if best_score is None or val > best_score:
            best_score = val
            best_move = [dx, dy]

    # Fallback: if all moves blocked, return stay (must be legal per validator; attempt stay if possible).
    if best_score is None:
        return [0, 0] if inb(sx, sy) else [dx for dx, dy in moves if inb(sx + dx, sy + dy)][0:1] or [0, 0]
    return best_move