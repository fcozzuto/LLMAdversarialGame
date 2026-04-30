def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    possible = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                possible.append((0, 0))
            else:
                possible.append((dx, dy))

    # Choose target that maximizes advantage in taking it soon.
    # Advantage = (opp_dist - self_dist), tie: smaller self_dist, then deterministic.
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev (diagonal allowed)

    # Predict a "priority" resource for changing strategy across turns deterministically
    parity_flip = (observation.get("turn_index", 0) % 2)
    res_order = []
    for r in resources:
        res_order.append(r)
    # Deterministic reorder: alternate between near-first and far-first by parity
    if parity_flip == 0:
        res_order.sort(key=lambda r: (dist((sx, sy), r), r[0], r[1]))
    else:
        res_order.sort(key=lambda r: (-dist((sx, sy), r), r[0], r[1]))

    # Preselect best resource under current position (for tie-breaking on moves)
    best_adv = None
    best_res = None
    for r in res_order:
        ad = dist((ox, oy), r) - dist((sx, sy), r)
        if best_adv is None or ad > best_adv or (ad == best_adv and (dist((sx, sy), r), r[0], r[1]) < (dist((sx, sy), best_res), best_res[0], best_res[1])):
            best_adv = ad
            best_res = r

    tx, ty = best_res
    best_score = None
    best_move = (0, 0)

    for dx, dy in possible:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Primary: move increases immediate advantage for the selected target
        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Secondary: if tied, prefer moves that reduce distance to opponent (to contest space)
        contest = dist((nx, ny), (ox, oy))
        # Tertiary: encourage moving toward other resources if target is blocked/contested
        other_best = None
        for r in res_order[:4]:  # small deterministic look
            val = dist((ox, oy), r) - dist((nx, ny), r)
            if other_best is None or val > other_best:
                other_best = val

        score = (opp_d - self_d, -contest, other_best)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]