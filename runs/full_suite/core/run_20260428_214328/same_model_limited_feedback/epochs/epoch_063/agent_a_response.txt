def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick a target where we have the biggest distance advantage over the opponent
    best_r = None
    best_key = None
    for r in resources:
        if r == [sx, sy]:
            continue
        rv = (r[0], r[1])
        sd = dist2((sx, sy), rv)
        od = dist2((ox, oy), rv)
        diff = sd - od  # negative => we are closer
        key = (diff, sd)  # smaller diff first, then closer
        if best_key is None or key < best_key:
            best_key = key
            best_r = rv
    if best_r is None:
        best_r = (sx, sy)

    tx, ty = best_r

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if len(moves) == 0:
        return [0, 0]

    # Evaluate each possible move deterministically
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = dist2((nx, ny), (tx, ty))
        op_d = dist2((ox, oy), (tx, ty))

        # Also encourage moving along the direct line to the target
        align = -((nx - tx) * (sx - tx) + (ny - ty) * (sy - ty))

        # Strongly prioritize capturing/approaching; also try to keep opponent from the target
        # Use opponent distance *after we move* only via our change: assume opponent continues toward target,
        # so reward moves that increase our relative access (my_d - op_d).
        rel = my_d - op_d

        # If our move grabs a resource (likely), my_d becomes 0
        score = (my_d, rel, align)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]