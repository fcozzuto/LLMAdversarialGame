def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_penalty(nx, ny):
        if (nx, ny) in obstacles:
            return -5000
        return 0

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Intercept: assume opponent races their nearest resource; move to steal it.
    opp_target = None
    best_od = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < best_od:
            best_od = d
            opp_target = (rx, ry)
    itx, ity = opp_target

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        base = cell_penalty(nx, ny)

        # Race component: maximize advantage at next cell over all resources.
        race = -10**18
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            lead = d_opp - d_me
            val = lead * 1000 - d_me + 0.01 * d_opp
            if val > race:
                race = val

        # Steal component: reduce distance to opponent's nearest resource.
        steal = -man(nx, ny, itx, ity) + 0.005 * best_od

        score = base + race + steal
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]