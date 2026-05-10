def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    if not resources:
        # deterministic "sweep" toward center-ish
        tx, ty = w // 2, h // 2
    else:
        best_steal = None
        best_race = None
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < od:
                # Race: prefer shortest self time; break ties by maximizing (od-sd)
                key = (sd, -(od - sd), rx, ry)
                if best_race is None or key < best_race[0]:
                    best_race = (key, (rx, ry))
            # If we can't beat them, try to steal what they are closest to
            key2 = (od, sd, rx, ry)
            if best_steal is None or key2 < best_steal[0]:
                best_steal = (key2, (rx, ry))

        target = best_race[1] if best_race is not None else best_steal[1]
        tx, ty = target[0], target[1]

    best = (10**9, 0, 0)
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # primary: reduce distance to target; secondary: avoid moving away from target
        self_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        key = (self_d, opp_d, -dx, -dy)
        if key < best:
            best = key
            best_move = [dx, dy]
    return best_move