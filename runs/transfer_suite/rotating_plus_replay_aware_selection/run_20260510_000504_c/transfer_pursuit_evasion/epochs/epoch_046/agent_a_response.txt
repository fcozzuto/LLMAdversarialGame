def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer and (("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role)):
        i_am_pursuer = False
    if not i_am_pursuer:
        # if role unclear, prefer pursuer behavior as safer in pursuit_evasion
        i_am_pursuer = True

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obst_near(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    c += 1
        return c

    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        manh = abs(ddx) + abs(ddy)
        on = obst_near(nx, ny)

        # deterministic tie-breaks by using a fixed ordering of comparisons
        if i_am_pursuer:
            key = (dist2, manh, on, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        else:
            key = (-dist2, -manh, on, -nx, -ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]