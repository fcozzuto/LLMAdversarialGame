def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a contest target: prefer resources where we are at least as close as opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # key: prefer we are no worse, then maximize margin (od-sd), then smaller sd
        # also include resource coords to break ties deterministically
        if sd <= od:
            key = (0, -(od - sd), sd, rx, ry)
        else:
            # if we're worse, still consider but deprioritize
            key = (1, -(sd - od), od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Evaluate candidate moves by resulting contest advantage and progress to target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue

        # If we step onto any resource, prioritize immediately.
        on_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break

        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Key aims: immediate resource first; then contest advantage opp_d-self_d;
        # then smaller self distance to the target; then avoid getting too close to opponent generally.
        contest = opp_d - self_d
        opp_prox = man(nx, ny, ox, oy)
        val = (-(on_res), -contest, self_d, opp_prox, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]