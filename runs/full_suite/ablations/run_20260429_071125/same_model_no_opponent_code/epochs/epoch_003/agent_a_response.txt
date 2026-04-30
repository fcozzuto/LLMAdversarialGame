def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # If we're already on a resource, stay is allowed; otherwise proceed normally.
    if (x, y) in obstacles:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None

    # Pick a "competitive" target set: resources we are no farther from than opponent.
    # If none, fall back to nearest resource.
    competitive = []
    for r in resources:
        myd = dist((x, y), r)
        opd = dist((ox, oy), r)
        if myd <= opd:
            competitive.append((myd, r, opd))
    targets = competitive if competitive else [(dist((x, y), r), r, dist((ox, oy), r)) for r in resources]

    # Deterministic innovation: slight preference alternating by epoch/turn.
    bias = 0.04 if (observation["turn_index"] % 2 == 0) else -0.04

    for dx, dy in legal:
        nx, ny = x + dx, y + dy

        # If we step onto a resource, heavily prefer.
        step_on_resource = 1.0 if (nx, ny) in resources else 0.0

        # Evaluate best resource we can reach next.
        best_my_next = None
        best_gain = None
        for myd, r, opd in targets:
            myd2 = dist((nx, ny), r)
            if best_my_next is None or myd2 < best_my_next:
                best_my_next = myd2
            # gain favors us being closer than opponent to that resource
            gain = (opd - myd2) - 0.25 * myd2
            if best_gain is None or gain > best_gain:
                best_gain = gain

        if best_my_next is None:
            # no resources
            my_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            oxd = dist((nx, ny), (ox, oy))
            score = my_center - 0.15 * oxd + bias * (nx - ox)
        else:
            # Lower is better: combine approach distance to best target, avoid opponent, and block slight.
            my_to_target = best_my_next
            oxd = dist((nx, ny), (ox, oy))
            # Encourage reducing opponent's advantage to the best gain resource.
            score = (my_to_target
                     - 0.28 * oxd
                     - 0.55 * best_gain
                     - 2.2 * step_on_resource)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]