def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set((x, y) for x, y in resources)
    if not resources:
        return [0, 0]

    # Predict opponent's immediate intent: nearest resource (nearest_resource archetype)
    opp_target = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        key = (d, rx, ry)
        if opp_target is None or key < opp_target[0]:
            opp_target = (key, (rx, ry))
    tx, ty = opp_target[1]

    # Opponent predicted move toward its target (greedy step)
    best_od = None
    opp_next = (ox, oy)
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not valid(nx, ny):
            continue
        od = man(nx, ny, tx, ty)
        key = (od, nx, ny)
        if best_od is None or key < best_od:
            best_od = key
            opp_next = (nx, ny)
    opx, opy = opp_next

    # Choose our move to create/maintain capture advantage vs predicted opponent next step
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # If we capture now, strongly prefer (unless opponent captures same resource simultaneously)
        capture_now = (nx, ny) in res_set
        opp_capture_now = (opx, opy) in res_set and (opx, opy) == (nx, ny)
        if capture_now and not opp_capture_now:
            key = (-1000000, 0, nx, ny)
        else:
            # Target either the opponent's target or the closest remaining resource to us
            my_target = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                key2 = (d, rx, ry)
                if my_target is None or key2 < my_target[0]:
                    my_target = (key2, (rx, ry))
            mx, my = my_target[1]
            myd = man(nx, ny, mx, my)
            opd = man(opx, opy, mx, my)
            # Prefer increasing (opd - myd): we want opponent further than us after their step
            # Also discourage moving closer to opponent when not capturing
            key = (-(opd - myd), myd, man(nx, ny, opx, opy), nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]