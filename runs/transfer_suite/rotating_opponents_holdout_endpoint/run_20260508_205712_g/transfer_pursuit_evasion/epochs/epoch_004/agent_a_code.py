def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(a[0]), int(a[1])) for a in obstacles if len(a) >= 2}

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("pred" in self_role)
    evader = ("evad" in self_role) or ("run" in self_role) or ("esc" in self_role)
    if not pursuer and not evader:
        pursuer = False  # default to evasion against pursuit_direct-like behavior

    def neighbors_count(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if valid(nx, ny):
                c += 1
        return c

    best_move = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = neighbors_count(nx, ny)

        if pursuer:
            # Minimize distance; avoid getting boxed in.
            score = (-d2 * 1000) + (mob * 10) + (-(abs(nx-ox) + abs(ny-oy)) * 2)
        else:
            # Maximize distance; prefer corners and avoid boxing in.
            corner_bias = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)
            score = (d2 * 1000) + (mob * 10) + (corner_bias * 3)

        # Deterministic tie-break: lexicographic dx,dy preference.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]