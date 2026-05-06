def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v): 
        return 0 if v == 0 else (1 if v > 0 else -1)

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Pick target: prefer states where we are closer than opponent (lead), then closer overall.
    best_t = None
    best_tv = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me + d_opp * 0.01
        if best_tv is None or tv > best_tv or (tv == best_tv and (tx, ty) < best_t):
            best_tv, best_t = tv, (tx, ty)

    tx, ty = best_t

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            continue
        # Make progress to target, keep advantage vs opponent, lightly penalize moving away.
        d_me2 = abs(tx - nx) + abs(ty - ny)
        d_opp2 = abs(tx - ox) + abs(ty - oy)
        # Bonus if we can grab resource this step.
        grab = 1 if (nx, ny) in obstacles else 0
        tv = (d_opp2 - d_me2) * 1000 - d_me2 + d_opp2 * 0.01
        tv += -0.2 * (abs(nx - x) + abs(ny - y))  # mild preference to shorter adjustments
        # If still tied, prefer deterministic ordering by direction after score.
        if best_s is None or tv > best_s or (tv == best_s and (dx, dy) < best_move):
            best_s, best_move = tv, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]