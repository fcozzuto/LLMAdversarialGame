def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Deterministic tie-break preference ordering
    order = {(-1, -1): 0, (-1, 0): 1, (-1, 1): 2, (0, -1): 3, (0, 0): 4, (0, 1): 5, (1, -1): 6, (1, 0): 7, (1, 1): 8}

    best = (10**18, 10**18, 10**18, 10**18)  # will be minimized
    best_move = (0, 0)

    if is_pursuer:
        # Greedy chase with obstacle bias: prefer moves that reduce squared distance.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = d2(nx, ny, ox, oy)
            # Bias toward keeping mobility (fewer dead-ends) while closing.
            free = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    free += 1
            key = (0 if dist == 0 else 1, dist, -free, order[(dx, dy)])
            if key < best:
                best = key
                best_move = (dx, dy)
    else:
        # Evader: run to maximize distance; avoid stepping into opponent-aligned corridor by preferring
        # moves that increase "escape" along the dominant axis relative to opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = d2(nx, ny, ox, oy)

            # Escape axis score: move away more in the axis where opponent is farther.
            away_x = nx - ox
            away_y = ny - oy
            axis = 1 if abs(away_x) >= abs(away_y) else 0
            axis_score = (abs(away_x) if axis else abs(away_y))

            # Mobility and determinism
            free = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    free += 1
            # Also discourage moving into positions that make the opponent closer next move (one-ply look).
            worst_next = -10**18
            for odx, ody in moves:
                tox, toy = ox + odx, oy + ody
                if not legal(tox, toy):
                    continue
                worst_next = max(worst_next, -d2(tox, toy, nx, ny))

            # Minimize a cost (negative of desired terms)
            cost = (-dist, -axis_score, -(free + worst_next * 1e-6), order[(dx, dy)])
            if cost < best:
                best = cost
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]