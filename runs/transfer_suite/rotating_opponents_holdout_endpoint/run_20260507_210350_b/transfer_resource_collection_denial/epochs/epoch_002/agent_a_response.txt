def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        # Pick a target that we can reach sooner than the opponent, tie-breaking by coordinates.
        best_t = None
        best_key = None
        for r in resources:
            if r in obstacles:
                continue
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            key = (ds - do, ds, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best_t = r
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # If target is completely surrounded by obstacles, fall back to next best resource.
    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    step_candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        step_candidates.append((nx, ny, dx, dy))
    if not step_candidates:
        return [0, 0]

    # Score moves: approach target while also blocking opponent's race to resources.
    opp_immediates = []
    for r in resources:
        if r in obstacles:
            continue
        opp_immediates.append((dist((ox, oy), r), r[0], r[1], r))
    opp_immediates.sort()
    top_opp = opp_immediates[0][3] if opp_immediates else (tx, ty)

    best_move = None
    best_score = None
    for nx, ny, dx, dy in step_candidates:
        my_d = dist((nx, ny), (tx, ty))
        my_close_to_opp = dist((nx, ny), top_opp)
        # Prefer capturing resources by stepping onto them, and deny opponent by increasing their advantage.
        score = my_d
        # Lower is better: make opponent distance to our target worse relative to us
        opp_d_on_target = dist((ox, oy), (tx, ty))
        # If we step onto target now, strongly prioritize.
        if (nx, ny) == (tx, ty):
            score -= 1000
        # Otherwise, still prioritize being closer than opponent.
        score += 0.35 * dist((ox, oy), (tx, ty)) - 0.65 * my_d
        # And avoid moves that let us become worse for contesting the opponent's most likely resource.
        score += 0.10 * my_close_to_opp
        # Deterministic tie-break: lexicographic by (nx, ny)
        key = (score, nx, ny)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]