def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Fallback if no resources
    if not resources:
        return [0, 0]

    # Pick target: prefer resources where we are closer; otherwise pick best "steal/intercept" option
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # secure_gain positive when we can reach earlier
        secure_gain = op_d - my_d
        # tie-break: closer to us, and further from opponent when possible
        key = (
            0 if secure_gain > 0 else 1,           # prefer secure first
            -secure_gain,                            # larger gain first
            my_d,                                    # then closer to us
            -dist(ox, oy, rx, ry),                  # then far from opponent
            rx, ry                                   # deterministic
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move one step toward target (allow diagonals), avoid obstacles, deterministic tie-break
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_mv_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_next = dist(nx, ny, tx, ty)
        op_d_to_target = dist(ox, oy, tx, ty)
        # prefer reducing our distance to target; if equal, prefer states that keep us ahead vs opponent
        key = (
            my_next,
            -(op_d_to_target - my_next),
            abs(nx - tx) + abs(ny - ty),
            nx, ny,
        )
        if best_mv_key is None or key < best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]