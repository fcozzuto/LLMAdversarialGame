def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    myx, myy = observation["self_position"]
    opx, opy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return myx, myy
        if (nx, ny) in obstacles:
            return myx, myy
        return nx, ny

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # fallback: drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, (0, 0))
        for dx, dy in deltas:
            nx, ny = clamp(myx + dx, myy + dy)
            score = -dist((nx, ny), (tx, ty))
            if score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_score = -10**9
    # for each move, pick the resource that gives best relative advantage
    for dx, dy in deltas:
        nx, ny = clamp(myx + dx, myy + dy)
        # also consider picking up immediately: distance becomes 0
        best_res = None
        best_res_score = -10**9
        for rx, ry in resources:
            md = dist((nx, ny), (rx, ry))
            od = dist((opx, opy), (rx, ry))
            # prefer resources we reach sooner than opponent; break ties by closeness
            res_score = (od - md) * 100 - md
            if res_score > best_res_score:
                best_res_score = res_score
                best_res = (rx, ry, md, od)
        # secondary: slight preference to reduce our distance to the current best target
        total_score = best_res_score
        if total_score > best_score:
            best_score = total_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]