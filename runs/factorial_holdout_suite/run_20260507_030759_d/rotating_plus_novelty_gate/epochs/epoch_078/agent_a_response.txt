def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    if not res:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    my = (sx, sy)
    opp = (ox, oy)
    oppD = md(my, opp)

    # Strongly prefer resources where we are ahead in shortest-path race.
    best_r = None
    best_key = None
    for r in res:
        dm = md(my, r)
        do = md(opp, r)
        # primary: (do - dm) big means opponent farther; also penalize our distance slightly.
        key = ((do - dm) * 1000 - dm, -dm, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r

    # If opponent is very close overall, use a defensive bias away from opponent while still progressing.
    defensive = oppD <= 2

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in legal:
        nm = (nx, ny)
        dm = md(nm, best_r)
        do = md(opp, best_r)
        # progress to target: minimize dm; win race: maximize (do - dm)
        race = (do - dm) * 1000
        prog = -dm
        # optional defensive: avoid getting closer to opponent
        if defensive:
            closeness = -md(nm, opp)  # higher when farther due to negative sign
        else:
            closeness = 0
        # deterministic tie-break: favor smaller dx,dy magnitude then coordinates.
        tie = (-abs(dx) - abs(dy), -nx, -ny)
        key = (race + prog + closeness, tie)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]